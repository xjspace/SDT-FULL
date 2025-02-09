class TTSException(Exception):
    """TTS服务基础异常"""
    def __init__(self, service: str, message: str):
        super().__init__(f"[{service}] {message}")
        self.service = service
        self.message = message

class TTSConfigError(TTSException):
    """配置参数异常"""
    def __init__(self, service: str, missing_params: list):
        super().__init__(service, f"缺少必要配置参数: {', '.join(missing_params)}")

class TTSVoiceNotFound(TTSException):
    """声音资源未找到异常"""
    def __init__(self, service: str, voice_id: str):
        super().__init__(service, f"未找到指定声音: {voice_id}")

class TTSRateLimitExceeded(TTSException):
    """API调用频率限制异常"""
    def __init__(self, service: str, reset_time: int):
        super().__init__(service, f"API调用超限，重置时间: {reset_time}秒")

class TTSSynthesisError(TTSException):
    """语音合成失败异常"""
    def __init__(self, service: str, status_code: int):
        super().__init__(service, f"语音合成失败，状态码: {status_code}")
