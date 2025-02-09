import requests
import json
import logging
from pathlib import Path
from typing import Optional
from vosk import Model, KaldiRecognizer
from transformers import pipeline

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, config: dict):
        self.config = config
        self._init_models()

    def _init_models(self):
        """初始化语音处理模型"""
        # 加载Vosk语音识别模型
        self.vosk_model = Model(self.config['model_paths']['vosk'])

        # 加载Hugging Face文本处理模型
        self.summarizer = pipeline(
            "summarization",
            model=self.config['model_paths']['summarization']
        )

        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=self.config['model_paths']['sentiment']
        )

    def download_audio(self, url: str, save_path: Path) -> bool:
        """下载音频文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"音频下载成功: {save_path.name}")
            return True

        except Exception as e:
            logger.error(f"音频下载失败: {str(e)}")
            return False

    def transcribe_audio(self, audio_path: Path) -> Optional[str]:
        """语音转写为文本"""
        try:
            recognizer = KaldiRecognizer(self.vosk_model, 16000)

            with open(audio_path, 'rb') as f:
                data = f.read(4096)
                while data:
                    recognizer.AcceptWaveform(data)
                    data = f.read(4096)

            result = json.loads(recognizer.FinalResult())
            return result['text']

        except Exception as e:
            logger.error(f"语音转写失败: {str(e)}")
            return None

    def process_text(self, text: str) -> dict:
        """文本处理流水线"""
        processed = {
            'summary': self._summarize_text(text),
            'sentiment': self._analyze_sentiment(text),
            'key_points': self._extract_key_points(text)
        }
        return processed

    def _summarize_text(self, text: str) -> str:
        """生成文本摘要"""
        return self.summarizer(
            text,
            max_length=self.config['processing']['summary_max_length'],
            min_length=self.config['processing']['summary_min_length'],
            do_sample=False
        )[0]['summary_text']

    def _analyze_sentiment(self, text: str) -> dict:
        """情感分析"""
        return self.sentiment_analyzer(text)[0]

    def _extract_key_points(self, text: str) -> list:
        """提取关键点（示例实现）"""
        # 实际应根据需求实现更复杂的逻辑
        return [sentence.strip() for sentence in text.split('.')[:3] if sentence]
