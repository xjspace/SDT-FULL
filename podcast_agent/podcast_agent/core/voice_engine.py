from pathlib import Path
import logging
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import os

class VoiceEngine:
    """音频后期处理引擎"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.default_intro = Path("assets/intro.mp3")
        self.default_outro = Path("assets/outro.mp3")

    def post_process(
        self,
        audio_file: Path,
        output_path: Path,
        intro: bool = True,
        outro: bool = True,
        normalize_db: float = -20.0
    ) -> Path:
        """音频后期处理流水线"""
        try:
            # 加载原始音频
            audio = AudioSegment.from_file(audio_file)
            self.logger.info(f"加载音频文件: {audio_file}, 时长: {len(audio)/1000:.1f}s")

            # 1. 标准化处理
            audio = self._apply_normalization(audio, normalize_db)

            # 2. 动态范围压缩
            audio = compress_dynamic_range(audio)

            # 3. 添加片头片尾
            if intro:
                audio = self._add_intro(audio)
            if outro:
                audio = self._add_outro(audio)

            # 4. 淡入淡出处理
            audio = audio.fade_in(1000).fade_out(2000)

            # 导出最终文件
            output_path.parent.mkdir(parents=True, exist_ok=True)
            audio.export(output_path, format="mp3", bitrate="192k")

            self.logger.info(f"后期处理完成，输出文件: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"音频处理失败: {str(e)}")
            raise

    def _apply_normalization(self, audio: AudioSegment, target_db: float) -> AudioSegment:
        """应用音频标准化"""
        self.logger.info(f"应用音频标准化 (目标: {target_db}dBFS)")
        return normalize(audio, headroom=abs(target_db))

    def _add_intro(self, audio: AudioSegment) -> AudioSegment:
        """添加片头音乐"""
        if self.default_intro.exists():
            intro = AudioSegment.from_file(self.default_intro)
            return intro.append(audio, crossfade=1500)
        return audio

    def _add_outro(self, audio: AudioSegment) -> AudioSegment:
        """添加片尾音乐"""
        if self.default_outro.exists():
            outro = AudioSegment.from_file(self.default_outro)
            return audio.append(outro, crossfade=1500)
        return audio

    @staticmethod
    def convert_sample_rate(audio: AudioSegment, target_rate: int = 44100) -> AudioSegment:
        """转换采样率"""
        return audio.set_frame_rate(target_rate)
