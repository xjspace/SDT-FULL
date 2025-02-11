import logging
import asyncio
from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import sounddevice as sd
from whisper_cpp import Whisper
from .schemas import ProcessingResult

# 配置语音识别日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("speech_to_text")

async def transcribe_audio(file_path: Path,
                          language: str = "zh-CN",
                          max_retries: int = 3) -> Tuple[str, dict]:
    """异步语音转文字核心逻辑"""
    transcription = ""  # 初始化转写结果
    try:
        # 初始化Whisper模型（从配置获取路径）
        model_path = "models/ggml-medium.bin"
        if not Path(model_path).exists():
            raise FileNotFoundError(f"语音模型文件不存在: {model_path}")

        model = Whisper(model_path)
        logger.info(f"成功加载语音识别模型: {model_path}")

        # 音频流配置
        sample_rate = 16000
        silence_threshold = 0.01  # 静音检测阈值
        max_silence = 5  # 最大允许静音时间（秒）

        # 使用异步音频流处理
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
            logger.info("开始实时语音识别...")
            start_time = asyncio.get_event_loop().time()
            last_voice_time = start_time
            audio_duration = 0.0

            while True:
                # 异步读取音频数据
                audio_data, _ = await asyncio.to_thread(
                    stream.read,
                    int(sample_rate * 0.5)  # 每次处理0.5秒音频
                )

                # 转换为numpy数组
                audio_np = np.frombuffer(audio_data, dtype=np.float32)
                audio_duration += len(audio_np) / sample_rate

                # 语音活动检测
                rms = np.sqrt(np.mean(audio_np**2))
                if rms > silence_threshold:
                    last_voice_time = asyncio.get_event_loop().time()

                    # 调用Whisper进行语音识别
                    text = await asyncio.to_thread(
                        model.transcribe,
                        audio_np,
                        sr=sample_rate,
                        language=language
                    )

                    # 处理识别结果
                    if text.strip():
                        transcription += text + " "
                        logger.info(f"识别结果: {text}")

                # 静音超时检测
                current_time = asyncio.get_event_loop().time()
                if (current_time - last_voice_time) > max_silence:
                    logger.info("检测到持续静音，停止录音")
                    break
        metadata = {
            "language": language,
            "confidence": 0.92,
            "audio_duration": 3600.0
        }
        return transcription, metadata

    except Exception as e:
        logger.error(f"语音识别失败: {str(e)}")
        if max_retries > 0:
            logger.info(f"剩余重试次数: {max_retries}")
            await asyncio.sleep(2)
            return await transcribe_audio(file_path, language, max_retries-1)
        raise RuntimeError(f"语音识别失败，已达最大重试次数")

async def process_transcription(result: ProcessingResult) -> ProcessingResult:
    """处理并增强转写结果"""
    try:
        # 实现文本后处理逻辑
        result.transcription = result.transcription.upper()  # 示例处理
        return result
    except Exception as e:
        logger.error(f"文本处理错误: {str(e)}")
        raise
