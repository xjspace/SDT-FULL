"""
Azure TTS 集成测试（需有效订阅密钥）

测试前准备：
1. 设置环境变量：
   export AZURE_TTS_KEY="your-subscription-key"
   export AZURE_REGION="eastasia"
2. 确保网络连接正常
"""
import os
import pytest
from podcast_agent.core.tts.services.azure import AzureTTS
from podcast_agent.core.tts.exceptions import TTSException

@pytest.fixture
def live_tts():
    """使用环境变量配置创建真实TTS实例"""
    subscription_key = os.getenv("AZURE_TTS_KEY")
    region = os.getenv("AZURE_REGION")
    if not subscription_key or not region:
        pytest.skip("需要设置AZURE_TTS_KEY和AZURE_REGION环境变量")
    return AzureTTS(subscription_key=subscription_key, region=region)

class TestAzureTTSLive:
    """真实环境集成测试套件"""

    def test_successful_synthesis(self, live_tts):
        """测试基本语音合成功能"""
        audio_data = live_tts.synthesize("欢迎使用播客代理服务")
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 1000  # 确保获得有效音频数据

    def test_ssml_synthesis(self, live_tts):
        """测试SSML格式合成"""
        ssml = """<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
            <voice name='zh-CN-XiaoxiaoNeural'>
                当前温度<prosody pitch='high'>25度</prosody>
            </voice>
        </speak>"""
        audio_data = live_tts.synthesize(ssml)
        assert len(audio_data) > 2000

    def test_invalid_key_handling(self):
        """测试无效密钥异常处理"""
        with pytest.raises(TTSException):
            invalid_tts = AzureTTS(subscription_key="invalid-key", region="eastasia")
            invalid_tts.synthesize("测试文本")

    def test_long_text_rejection(self, live_tts):
        """测试超长文本拒绝"""
        long_text = "测试" * 2000  # 生成超过4000字符的文本
        with pytest.raises(ValueError):
            live_tts.synthesize(long_text)

if __name__ == "__main__":
    pytest.main(["-s", __file__])  # -s 参数显示print输出
