from pathlib import Path
import logging
from .config import TTSConfig
from .services.azure import AzureTTS
from .exceptions import InvalidConfigError, UnsupportedTTSTypeError

class TTSFactory:
    """TTS引擎工厂类"""

    @staticmethod
    def create_engine(config_path: Path = Path("config/tts_config.yaml")):
        """创建TTS引擎实例"""
        logger = logging.getLogger(__name__)

        try:
            # 加载配置文件
            config = TTSConfig.load_config(config_path)

            # 根据配置创建对应引擎
            if config["type"] == "azure":
                return AzureTTS(
                    subscription_key=config["azure"]["subscription_key"],
                    region=config["azure"]["region"]
                )

            raise UnsupportedTTSTypeError(f"不支持的TTS类型: {config['type']}")

        except FileNotFoundError:
            logger.error("配置文件不存在: %s", config_path)
            raise InvalidConfigError("缺少TTS配置文件")
        except KeyError as e:
            logger.error("配置参数缺失: %s", str(e))
            raise InvalidConfigError(f"缺少必要配置参数: {str(e)}")
