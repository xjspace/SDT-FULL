import aiohttp
import ffmpeg
import whisper
from pydub import AudioSegment
import tempfile
import os

async def process_podcast(url: str):
    """端到端播客处理流程"""
    try:
        # 1. 异步下载音频文件
        temp_audio = await download_audio(url)

        # 2. 转码为WAV格式
        wav_path = convert_to_wav(temp_audio)

        # 3. 语音识别带时间戳
        transcript = transcribe_with_timestamps(wav_path)

        return {
            "status": "success",
            "transcript": transcript,
            "temp_files": [temp_audio, wav_path]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # 清理临时文件
        for f in [temp_audio, wav_path]:
            if f and os.path.exists(f):
                os.remove(f)

async def download_audio(url: str) -> str:
    """异步下载音频文件"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                _, ext = os.path.splitext(url)
                fd, temp_path = tempfile.mkstemp(suffix=ext)
                with os.fdopen(fd, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return temp_path
            raise Exception(f"下载失败，状态码：{response.status}")

def convert_to_wav(input_path: str) -> str:
    """使用FFmpeg转码为WAV格式"""
    output_path = input_path + ".wav"
    (
        ffmpeg
        .input(input_path)
        .output(output_path, acodec='pcm_s16le', ac=1, ar='16000')
        .run(overwrite_output=True, quiet=True)
    )
    return output_path

def transcribe_with_timestamps(audio_path: str, language: str = "auto", model_size: str = "base") -> list:
    """多语言语音识别带时间戳"""
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(
            audio_path,
            word_timestamps=True,
            language=language if language != "auto" else None,
            task="transcribe"
        )
        return [{
        "text": segment['text'],
        "start": segment['start'],
        "end": segment['end']
    } for segment in result['segments']]
    except Exception as e:
        print(f"语音识别错误: {str(e)}")
        return []

def generate_summary(transcript: list[dict], max_length: int = 200) -> str:
    """生成播客内容摘要"""
    try:
        # 合并所有文本段落
        full_text = " ".join([seg['text'] for seg in transcript])

        # 基础摘要生成逻辑（后续可集成NLP模型）
        if len(full_text) <= max_length:
            return full_text

        # 简单截取前max_length个字符作为临时实现
        summary = full_text[:max_length].rsplit(' ', 1)[0] + "..."
        return summary
    except Exception as e:
        print(f"摘要生成错误: {str(e)}")
        return ""

# 添加函数别名保持兼容性
speech_to_text = transcribe_with_timestamps

def process_podcast_url(url: str):
    """处理播客URL的核心逻辑"""
    try:
        # 调用现有处理流程
        result = process_podcast(url)

        # 如果处理成功，添加摘要生成
        if result["status"] == "success":
            transcript = result["transcript"]
            summary = generate_summary(transcript)
            result["summary"] = summary

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"处理过程中发生错误: {str(e)}"
        }

__all__ = [
    'process_podcast_url',  # 导出声明已存在
    # ... 其他已有的导出项
]
