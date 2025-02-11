from pydub import AudioSegment
import logging
from pathlib import Path
from .exceptions import PodcastError

class AudioPipeline:
    def __init__(self, output_format="mp3", bitrate="192k"):
        self.output_format = output_format
        self.bitrate = bitrate
        self.logger = logging.getLogger(__name__)

    def convert_format(self, input_path, output_dir="processed"):
        """转换音频格式并标准化输出"""
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            audio = AudioSegment.from_file(input_path)
            output_path = Path(output_dir) / f"{Path(input_path).stem}.{self.output_format}"

            audio.export(output_path,
                        format=self.output_format,
                        bitrate=self.bitrate,
                        parameters=["-ar", "44100", "-ac", "2"])

            self.logger.info(f"音频处理完成: {output_path}")
            return str(output_path)
        except Exception as e:
            raise PodcastError(f"格式转换失败: {str(e)}") from e

    def split_audio(self, input_path, segment_length=600000):
        """按指定时长分割音频文件（单位：毫秒）"""
        try:
            audio = AudioSegment.from_file(input_path)
            segments = []
            output_dir = Path(input_path).parent / "segments"
            output_dir.mkdir(exist_ok=True)

            for i, start in enumerate(range(0, len(audio), segment_length)):
                end = start + segment_length
                segment = audio[start:end]
                segment_path = output_dir / f"{Path(input_path).stem}_part{i+1}.{self.output_format}"
                segment.export(segment_path, format=self.output_format)
                segments.append(str(segment_path))

            return segments
        except Exception as e:
            raise PodcastError(f"音频分割失败: {str(e)}") from e
