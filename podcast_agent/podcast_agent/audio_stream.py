import yaml
import sounddevice as sd
import numpy as np
from webrtcvad import Vad
from whisper import load_model

class AudioStreamProcessor:
    def __init__(self, config_path="config/audio_stream.yaml"):
        import platform
        import logging
        from pathlib import Path

        # 增强Windows日志路径处理
        log_path = Path('podcast_agent.log').resolve()
        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8' if platform.system() == 'Windows' else None
        )

        try:
            # 配置文件加载（增加Windows路径格式校验）
            if not config_path.endswith(('.yaml', '.yml')):
                raise ValueError("仅支持YAML配置文件")

            with open(config_path, encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # 参数校验（Windows音频设备兼容性）
            self.sample_rate = int(self.config.get('sample_rate', 16000))
            self.channels = int(self.config.get('channels', 1))
            self.dtype = np.dtype(self.config.get('dtype', 'int16'))

            # 增强VAD参数校验（Windows兼容）
            # 初始化VAD（WebRTC VAD构造函数只需要模式参数）
            self.vad = Vad(int(self.config.get('vad_mode', 2)))
            # WebRTC VAD仅支持16kHz，强制设置采样率
            self.sample_rate = 16000
            logging.warning("WebRTC VAD强制设置采样率为16000Hz")

            # 记录系统信息
            logging.info(f"系统平台: {platform.system()} {platform.release()}")
            logging.info(f"音频配置: {self.config}")

        except Exception as e:
            logging.error(f"初始化失败: {str(e)}")
            raise RuntimeError(f"音频处理器初始化异常: {str(e)}")

        # 增强whisper模型加载（Windows路径处理）
        try:
            model_path = Path(self.config.get('whisper_model', 'base')).expanduser()
            self.whisper = load_model(str(model_path))
            logging.info(f"成功加载语音识别模型: {model_path}")
        except Exception as e:
            logging.error(f"模型加载失败: {str(e)}")
            raise RuntimeError("语音识别引擎初始化失败")

        # 初始化Windows音频设备（增强兼容性）
        if platform.system() == 'Windows':
            try:
                sd.default.device = self._get_windows_input_device()
                logging.info(f"已选择音频输入设备: {sd.default.device}")
            except Exception as e:
                logging.error(f"音频设备初始化失败: {str(e)}")
                raise RuntimeError("Windows音频设备配置异常")

    def _get_windows_input_device(self):
        """获取Windows系统下兼容的音频输入设备"""
        import logging
        devices = sd.query_devices()
        logging.info(f"检测到{len(devices)}个音频设备")

        # 构建候选设备列表（按优先级排序）
        candidate_devices = []
        for index, dev in enumerate(devices):
            if dev['max_input_channels'] < 1:
                continue  # 跳过无输入通道设备

            # Windows特定设备过滤（排除虚拟声卡）
            if 'virtual' in dev['name'].lower() or 'mme' not in dev['name'].lower():
                logging.debug(f"跳过虚拟设备: {dev['name']}")
                continue

            # 采样率兼容性检查（支持16k/44.1k/48k）
            supported_rates = [16000, 44100, 48000]
            actual_rate = int(dev['default_samplerate'])
            closest_rate = min(supported_rates, key=lambda x: abs(x - actual_rate))

            candidate_devices.append({
                'index': index,
                'name': dev['name'],
                'rate': closest_rate,
                'channels': dev['max_input_channels'],
                'is_default': dev['isdefault']
            })

        # 按优先级排序：采样率匹配度 > 通道数 > 是否默认设备
        candidate_devices.sort(
            key=lambda x: (
                -1 if x['rate'] == 16000 else 0,  # 优先16kHz
                -x['channels'],  # 通道数多的优先
                -x['is_default']  # 默认设备优先
            ),
            reverse=False
        )

        if not candidate_devices:
            logging.error("未找到符合要求的音频输入设备")
            raise RuntimeError("无可用音频输入设备")

        # 选择最佳设备并记录
        best_device = candidate_devices[0]
        logging.info(f"选择音频设备: {best_device['name']} (采样率: {best_device['rate']}Hz)")

        # 设置实际使用的采样率
        self.sample_rate = best_device['rate']
        return best_device['index']
