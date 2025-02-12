from pathlib import Path
from typing import Dict, Any
from .content_generator import ContentGenerator
from .voice_engine import VoiceEngine
from .tts import TTSFactory, TTSConfigManager
import logging

class PodcastProducer:
    """播客生产流水线"""

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.content_gen = ContentGenerator()
        self.voice_engine = VoiceEngine()

        # 加载TTS配置
        try:
            self.tts_config = TTSConfigManager.load_config(config)
            self.tts_service = TTSFactory.create(
                service_type=self.tts_config.service_type,
                api_key=self.tts_config.api_key,
                **self.tts_config.voice_params
            )
        except Exception as e:
            self.logger.error(f"TTS服务初始化失败: {str(e)}")
            raise

    def produce_episode(self, topic: str, output_path: Path) -> Path:
        """完整生产流水线"""
        try:
            # 1. 生成内容
            script = self.content_gen.generate_script(topic)
            self.logger.info(f"生成播客脚本，长度: {len(script)}字符")

            # 2. 语音合成
            audio_file = self.tts_service.synthesize(
                text=script,
                output_format=self.tts_config.output_format,
                sampling_rate=self.tts_config.sampling_rate
            )
            self.logger.info(f"语音合成完成，文件路径: {audio_file}")

            # 3. 后期处理
            final_output = self.voice_engine.post_process(
                audio_file=audio_file,
                output_path=output_path
            )

            return final_output

        except Exception as e:
            self.logger.error(f"播客生产失败: {str(e)}")
            raise

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> bool:
        """验证配置文件有效性"""
        try:
            TTSConfig(**config)
            return True
        except Exception as e:
            return False
