from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class TTSBase(ABC):
    """TTS服务抽象基类（统一多服务接口）"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.validate_config(**kwargs)
        self._voices: Optional[List[Dict]] = None

    @abstractmethod
    def validate_config(self, **kwargs) -> None:
        """验证服务配置有效性"""
        pass

    @abstractmethod
    def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """文本转语音核心方法"""
        pass

    @abstractmethod
    def get_voices(self, refresh: bool = False) -> List[Dict]:
        """获取支持的声音列表（带缓存机制）"""
        pass

    @abstractmethod
    def get_voice_params(self, voice: str) -> Dict:
        """获取声音的详细参数配置"""
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """服务名称标识"""
        pass

    def __repr__(self) -> str:
        return f"<{self.service_name} TTS Service>"
