from pathlib import Path
import logging
import yaml
from typing import Dict, Any
from .exceptions import InvalidConfigError

class TTSConfig:
    """TTS配置管理类"""

    @staticmethod
    def load_config(config_path: Path = Path("config/tts_config.yaml")) -> Dict[str, Any]:
        """加载并验证配置文件"""
        logger = logging.getLogger(__name__)

        if not config_path.exists():
            logger.error("配置文件不存在: %s", config_path)
            raise FileNotFoundError(f"TTS配置文件未找到: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 验证必要配置项
            required_keys = ['type', 'azure']
            for key in required_keys:
                if key not in config:
                    raise InvalidConfigError(f"缺少必要配置项: {key}")

            # 验证Azure配置
            azure_required = ['subscription_key', 'region']
            for key in azure_required:
                if key not in config['azure']:
                    raise InvalidConfigError(f"Azure配置缺少必要项: {key}")

            return config

        except yaml.YAMLError as e:
            logger.error("配置文件解析失败: %s", str(e))
            raise InvalidConfigError("配置文件格式错误") from e
