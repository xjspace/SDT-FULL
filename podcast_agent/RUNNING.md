# 播客代理项目运行指南

## 先决条件
- Python 3.9+
- Node.js 16+
- FFmpeg 5+
- Azure认知服务订阅密钥（语音服务）

## 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/your-repo/podcast_agent.git
cd podcast_agent

# Windows 用户需要设置执行权限（PowerShell）
if ($env:OS -eq 'Windows_NT') {
  icacls start.sh /grant:r "%username%":RX
  Get-ChildItem scripts/*.sh | ForEach-Object { icacls $_.FullName /grant:r "%username%":RX }
}
```

### 2. 安装Python依赖
```bash
# 使用Poetry（推荐）
poetry install

# 或使用pip
pip install -r requirements.txt
```

### 3. 安装Node.js依赖
```bash
npm install
```

## 配置说明

### 核心配置文件
```yaml
# config/azure_tts.yaml
azure_cognitive:
  subscription_key: "your-azure-key"
  region: "eastasia"

# config/audio_stream.yaml
audio_settings:
  sample_rate: 16000
  channels: 1
  format: "S16_LE"
```

### 环境变量
```bash
# Linux/macOS
export AZURE_TTS_KEY="your-key"
export AUDIO_DEVICE="hw:1,0"

# Windows PowerShell
$env:AZURE_TTS_KEY="your-key"
$env:AUDIO_DEVICE="hw:1,0"
```

## 运行项目

### 开发模式
```bash
# 启动Python后端
poetry run python -m podcast_agent.core --dev

# 启动Web界面
npm run dev
```

### 生产模式
```bash
# Linux/macOS
./start.sh --prod

# Windows PowerShell
python -m podcast_agent.core --prod
```

### 混合模式（仅处理音频）
```bash
# 单独运行语音处理模块
poetry run python -m podcast_agent.core.voice_engine --input-device ${AUDIO_DEVICE}
```

## 服务端点
| 服务名称       | 端点地址                  | 协议    |
|----------------|--------------------------|---------|
| 语音合成服务   | http://localhost:5000/tts | HTTP    |
| 音频流服务     | ws://localhost:5001/stream| WebSocket |

## 常见问题排查

### 音频设备问题
```bash
# Linux
arecord -l

# Windows PowerShell
Get-PnpDevice -Class AudioEndpoint | Where-Object {$_.FriendlyName -like "*录音*"} | Format-List
```

### 依赖冲突解决
```bash
poetry update
npm audit fix
```

## 日志监控
```bash
# 实时查看日志（默认路径：g:/podcast_agent/logs/）
# Linux/macOS
tail -f logs/podcast_agent.log -n 100

# Windows PowerShell
Get-Content logs/podcast_agent.log -Wait -Tail 100

# 日志文件说明
# - podcast_agent.log : 主运行日志（DEBUG级别）
# - audio_processor.log : 音频处理日志
# - azure_tts.log : Azure语音服务交互日志
```

## 测试验证
```bash
# 运行Python测试
poetry run pytest tests/ -v

# 运行前端测试
npm test

# 音频处理测试 (需要连接音频设备)
poetry run python -m podcast_agent.core.voice_engine --test

# API接口测试
curl http://localhost:5000/tts/healthcheck
```

> 注意：首次运行前请确保已完成Azure服务凭证配置
