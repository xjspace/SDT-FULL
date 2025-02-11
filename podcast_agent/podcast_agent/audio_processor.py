import logging
import librosa
import numpy as np
from typing import Tuple, Optional, Dict
from pathlib import Path
from .schemas import ProcessingResult

# 配置音频处理日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("podcast_processor")

def denoise_audio(y: np.ndarray, sr: int) -> np.ndarray:
    """使用谱减法进行音频降噪"""
    stft = librosa.stft(y)
    magnitude = np.abs(stft)
    noise_profile = np.median(magnitude, axis=1, keepdims=True)
    denoised_magnitude = np.maximum(magnitude - noise_profile, 0)
    return librosa.istft(denoised_magnitude * np.exp(1j * np.angle(stft)))

async def load_audio(file_path: Path, max_duration: int = 3600) -> Tuple[np.ndarray, int]:
    """异步加载并预处理音频文件"""
    try:
        y, sr = librosa.load(file_path, sr=None, duration=max_duration)

        # 自动检测音频格式并转换
        if y.ndim > 1:
            y = librosa.to_mono(y)
        if sr != 16000:
            y = librosa.resample(y, orig_sr=sr, target_sr=16000)
            sr = 16000

        y = denoise_audio(y, sr)
        return y, sr
    except Exception as e:
        logger.error(f"Error loading audio: {str(e)}")
        raise RuntimeError(f"Audio processing failed: {str(e)}")

def segment_audio(y: np.ndarray, sr: int, segment_length: int = 300) -> list:
    """将长音频分段处理"""
    samples_per_segment = segment_length * sr
    return [y[i:i+samples_per_segment] for i in range(0, len(y), samples_per_segment)]

def extract_features(y: np.ndarray, sr: int) -> Dict[str, float]:
    """提取音频特征用于质量评估"""
    return {
        "snr": float(np.mean(y**2) / (np.var(y) + 1e-6)),
        "silence_ratio": float(np.mean(np.abs(y) < 0.01)),
        "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
        "rms_energy": float(np.mean(librosa.feature.rms(y=y)))
    }

async def analyze_audio_quality(file_path: Path) -> Dict[str, float]:
    """全面评估音频质量"""
    try:
        y, sr = await load_audio(file_path)
        features = extract_features(y, sr)

        # 添加基于经验的权重计算
        quality_score = (
            0.4 * (1 - features["silence_ratio"]) +
            0.3 * np.log(features["snr"] + 1) +
            0.2 * (features["spectral_centroid"] / 5000) +
            0.1 * features["rms_energy"]
        )

        features["quality_score"] = float(quality_score)
        return features
    except Exception as e:
        logger.error(f"Quality analysis failed: {str(e)}")
        raise
