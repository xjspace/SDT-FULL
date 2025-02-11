import whisper
import logging
from datetime import timedelta
from pathlib import Path
from .exceptions import PodcastError

class TranscriptGenerator:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.logger = logging.getLogger(__name__)
        self.model = None

    def load_model(self):
        """加载Whisper语音识别模型"""
        try:
            self.logger.info(f"正在加载Whisper {self.model_size}模型...")
            self.model = whisper.load_model(self.model_size)
            self.logger.info("模型加载完成")
        except Exception as e:
            raise PodcastError(f"模型加载失败: {str(e)}") from e

    def transcribe_audio(self, audio_path):
        """执行语音转文字操作"""
        if not self.model:
            self.load_model()

        try:
            self.logger.info(f"开始转录: {audio_path}")
            result = self.model.transcribe(audio_path)

            # 生成带时间戳的文本
            segments = [
                f"[{timedelta(seconds=seg['start'])}] {seg['text']}"
                for seg in result["segments"]
            ]

            # 保存原始转录结果
            raw_path = Path(audio_path).with_suffix('.txt')
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(segments))

            self.logger.info(f"转录完成: {raw_path}")
            return str(raw_path)

        except Exception as e:
            raise PodcastError(f"转录失败: {str(e)}") from e

    def generate_subtitles(self, audio_path, output_format="srt"):
        """生成字幕文件"""
        try:
            transcript_path = self.transcribe_audio(audio_path)
            srt_path = Path(transcript_path).with_suffix('.srt')

            with open(transcript_path, 'r', encoding='utf-8') as infile, \
                 open(srt_path, 'w', encoding='utf-8') as outfile:

                for i, line in enumerate(infile.readlines(), 1):
                    time_part, text = line.split('] ', 1)
                    start_time = time_part[1:]

                    outfile.write(f"{i}\n")
                    outfile.write(f"{start_time} --> {start_time}\n")
                    outfile.write(f"{text}\n\n")

            self.logger.info(f"字幕文件已生成: {srt_path}")
            return str(srt_path)

        except Exception as e:
            raise PodcastError(f"字幕生成失败: {str(e)}") from e
