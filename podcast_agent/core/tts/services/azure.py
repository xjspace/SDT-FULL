"""
Azure 文本转语音服务模块

提供与Azure Cognitive Services语音服务的集成，支持：
- 高质量中文语音合成
- 多种音频格式输出
- 自定义语音参数配置
- 完善的错误处理机制

典型工作流程：
1. 初始化TTS引擎
2. 配置语音参数
3. 执行文本合成
4. 获取音频数据或处理异常

示例用法：
>>> from podcast_agent.core.tts.services import AzureTTS
>>> tts = AzureTTS(subscription_key="your-key", region="eastasia")
>>> audio = tts.synthesize("欢迎收听今日新闻")
"""
import logging
from typing import Optional
from azure.cognitiveservices.speech import (SpeechConfig,
                                           SpeechSynthesisOutputFormat,
                                           SpeechSynthesizer,
                                           ResultReason)
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from ..exceptions import TTSException

class AzureTTS:
    """Azure文本转语音服务实现

    功能特性：
    - 支持中文语音合成
    - 默认使用MP3音频格式（48kHz/192kbps）
    - 异常处理与详细日志记录

    依赖要求：
    - azure-cognitiveservices-speech>=1.32.0
    - 有效的Azure语音服务订阅密钥

    使用示例：
    >>> tts = AzureTTS(subscription_key="your-key", region="eastasia")
    >>> audio_data = tts.synthesize("欢迎使用智能播客代理")
    """

    def __init__(self, subscription_key: str, region: str):
        """初始化TTS引擎

        Args:
            subscription_key: Azure语音服务订阅密钥
            region: 资源所属区域，例如"eastasia"

        日志配置：
        - 使用标准logging模块
        - 日志器名称：podcast_agent.core.tts.services.azure
        - 建议日志级别：INFO（基本操作） / DEBUG（详细流程）
        """
        self.subscription_key = subscription_key
        self.region = region
        self.logger = logging.getLogger(__name__)

        self.speech_config = SpeechConfig(
            subscription=subscription_key,
            region=region
        )
        self.speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
        )

    def synthesize(self, text: str, voice_name: str = "zh-CN-XiaoxiaoNeural") -> bytes:
        """执行语音合成并返回音频字节

        Args:
            text: 需要合成的文本内容（支持SSML格式）
            voice_name: 语音名称，默认为"晓晓"中文女声

        Returns:
            bytes: 音频字节数据（默认MP3格式）

        Raises:
            TTSException: 合成失败时抛出异常
            ValueError: 输入文本为空或超长（>4000字符）

        示例：
        >>> tts.synthesize("今日天气晴，气温25摄氏度", "zh-CN-YunyangNeural")
        b'...MP3音频数据...'
        >>> # SSML示例
        >>> ssml = \"\"\"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
        >>>     <voice name='zh-CN-XiaoxiaoNeural'>
        >>>         今天的温度是<prosody rate='+20%'>25度</prosody>
        >>>     </voice>
        >>> </speak>\"\"\"
        >>> tts.synthesize(ssml)
        """
        # 输入验证
        if not text.strip():
            raise ValueError("输入文本不能为空")
        if len(text) > 4000:
            raise ValueError("输入文本长度超过4000字符限制")

        try:
            # 配置语音参数
            self.speech_config.speech_synthesis_voice_name = voice_name
            synthesizer = SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )

            # 根据内容类型选择合成方法
            if text.strip().startswith("<speak"):
                self.logger.debug("使用SSML合成: %s...", text[:50])
                result = synthesizer.speak_ssml_async(text).get()
            else:
                self.logger.debug("合成普通文本: %s...", text[:50])
                result = synthesizer.speak_text_async(text).get()

            # 处理合成结果
            if result.reason == ResultReason.SynthesizingAudioCompleted:
                self.logger.info("语音合成成功 (时长: %.1fs)", result.audio_duration.total_seconds())
                return result.audio_data

            # 细化错误处理
            error_msg = f"合成失败: {result.reason}"
            if result.reason == ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg += f", 错误类型: {cancellation.error_details}"
                if cancellation.reason == cancellation.ErrorCode.TooManyRequests:
                    error_msg += " (API配额超限)"
            self.logger.error(error_msg)
            raise TTSException(error_msg)

        except ValueError as ve:
            self.logger.error("输入验证失败: %s", str(ve))
            raise
        except Exception as e:
            self.logger.exception("TTS服务异常 (语音: %s, 文本长度: %d)", voice_name, len(text))
            raise TTSException(f"Azure TTS服务异常：{str(e)}") from e
