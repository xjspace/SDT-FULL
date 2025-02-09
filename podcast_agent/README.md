# Podcast 智能处理代理

## 功能特性
- 多平台播客源自动下载
- 智能音频格式转换与优化
- 高精度语音转文字（支持中英文）
- 自动生成带时间轴的字幕文件
- 多线程任务处理

## 环境要求
- Python 3.8+
- FFmpeg 6.0 (需配置环境变量)
- Whisper语音识别模型

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基础使用
```python
from core.podcast import PodcastDownloader, AudioPipeline, TranscriptGenerator

# 下载播客
downloader = PodcastDownloader()
audio_file = downloader.download("https://example.com/podcast.mp3")

# 音频处理
processor = AudioPipeline()
processed_audio = processor.process(
    input_file=audio_file,
    output_format="wav",
    bitrate="192k"
)

# 生成字幕
transcriber = TranscriptGenerator()
transcript = transcriber.generate_transcript(
    audio_path=processed_audio,
    language="zh",
    output_srt=True
)
```

## 高级配置
```python
# 自定义下载设置
downloader.configure(
    max_retries=5,
    timeout=30,
    download_dir="./downloads"
)

# 启用GPU加速转录（需要CUDA环境）
transcriber.enable_gpu_acceleration()
```

## 命令行使用
```bash
# 下载单个播客
python cli.py download --url https://example.com/podcast.mp3

# 批量处理目录音频
python cli.py process --input-dir ./raw_audio --output-format mp3

# 生成双语字幕
python cli.py transcribe --audio podcast.wav --language zh --translate en
```

## 依赖管理
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 更新依赖版本
pip-upgrade requirements.txt
```

## 项目结构
```
/podcast_agent
├── core/            # 核心处理模块
├── docs/            # 开发文档
├── tests/           # 单元测试
├── cli.py           # 命令行入口
└── requirements.txt # 依赖清单
```

## 技术支持
遇到问题请提交issue至：
https://github.com/your-repo/podcast-agent/issues
