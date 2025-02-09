import logging
from datetime import datetime
from typing import Dict, Optional
import json

class PodcastContentEngine:
    def __init__(self, llm, max_retries=3):
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        self.max_retries = max_retries
        self.last_gen_time = 0.0

        # 初始化提示模板
        self.script_template = """根据以下要求生成播客脚本：
主题：{topic}
风格：{style}
结构要求：
1. 开场白（1分钟）
2. 主体内容（{duration}分钟）
3. 总结与互动提示（1分钟）

附加要求：
- 使用{style}风格的口语化表达
- 包含3个关键知识点
- 加入1个现实案例"""

    def generate_script(self, params: Dict) -> Optional[str]:
        """生成播客脚本核心逻辑"""
        start_time = datetime.now()
        retry_count = 0

        while retry_count < self.max_retries:
            try:
                # 构造完整提示词
                full_prompt = self._build_prompt(params)

                # 调用大模型
                response = self.llm.generate(
                    prompt=full_prompt,
                    temperature=0.7 if params.get("style") == "创意" else 0.3,
                    max_tokens=2000
                )

                # 后处理
                cleaned_script = self._postprocess_script(response.text)

                # 记录性能指标
                self.last_gen_time = (datetime.now() - start_time).total_seconds()

                return cleaned_script

            except Exception as e:
                self.logger.error(f"内容生成失败（尝试 {retry_count+1}/{self.max_retries}）: {str(e)}")
                retry_count += 1

        self.logger.error("达到最大重试次数，内容生成失败")
        return None

    def _build_prompt(self, params: Dict) -> str:
        """构建完整提示词"""
        duration = params.get("duration", 15)  # 默认15分钟节目
        return self.script_template.format(
            topic=params["topic"],
            style=params["style"],
            duration=duration-2  # 扣除开场和结尾时间
        )

    def _postprocess_script(self, raw_text: str) -> str:
        """脚本后处理"""
        # 去除多余空白
        cleaned = " ".join(raw_text.split())

        # 结构化校验
        sections = ["开场白", "主体内容", "总结与互动提示"]
        for section in sections:
            if section not in cleaned:
                self.logger.warning(f"脚本缺少必要章节: {section}")

        return cleaned

    def validate_script(self, script: str) -> bool:
        """脚本完整性验证"""
        required_elements = [
            "开场白", "关键知识点", "现实案例", "互动提示"
        ]
        return all(element in script for element in required_elements)
