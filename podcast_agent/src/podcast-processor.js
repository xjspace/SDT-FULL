const { EventEmitter } = require('events');
const { SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason } = require('@azure/ai-speech');
const { processWithClaude } = require('./ai-processor');
const { downloadAudio } = require('./network-utils');
const path = require('path');
const fs = require('fs').promises;
const logger = require('./logger');

class PodcastProcessor extends EventEmitter {
  constructor() {
    super();
    // 初始化状态跟踪
    this.STATES = {
      IDLE: 0,
      DOWNLOADING: 1,
      TRANSCRIBING: 2,
      PROCESSING: 3
    };
    this.currentState = this.STATES.IDLE;
  }

  async processPodcast(episodeUrl) {
    // 1. 下载音频文件
    const audioPath = await downloadAudio(episodeUrl);

    // 2. 初始化Azure语音识别配置
    const speechConfig = SpeechConfig.fromSubscription(
      process.env.AZURE_SPEECH_KEY,
      process.env.AZURE_SPEECH_REGION
    );
    let recognizer; // 将声明移到外部
    try {
      // 使用异步文件读取
      const audioData = await fs.readFile(audioPath);
      const audioConfig = AudioConfig.fromWavFileInput(audioData); // 添加音频配置
      recognizer = new SpeechRecognizer(speechConfig, audioConfig);

      // 3. 执行语音识别
      const transcription = await new Promise((resolve, reject) => {
        let result = '';
        recognizer.recognized = (_, e) => {
        if (e.result.reason === ResultReason.RecognizedSpeech) {
          result += e.result.text + '\n';
        }
      };

      // 初始化语音识别
      recognizer.startContinuousRecognitionAsync(
        () => logger.debug("语音识别开始"),
        err => reject(err)
      );

      // 注册会话结束事件
      // 合并sessionStopped事件处理
      recognizer.sessionStopped = () => {
        clearTimeout(timeoutId);
        recognizer.stopContinuousRecognitionAsync(
          () => {
            logger.debug("语音识别正常结束");
            resolve(result.trim());
          },
          stopErr => {
            logger.error(`停止识别失败: ${stopErr}`);
            reject(stopErr);
          }
        );
      };

      // 添加超时处理
      const timeoutId = setTimeout(() => {
        logger.warn("语音识别超时，强制停止");
        recognizer.stopContinuousRecognitionAsync(() => {
          reject(new Error("语音识别超时（30秒）"));
        });
      }, 30000);
    }); // 补全Promise闭合括号

    logger.info(`语音识别完成，内容长度：${transcription.length}字符`);
  } catch (error) {
    logger.error(`语音识别失败：${error.message}`);
    throw new Error(`语音处理失败: ${error.message}`);
  } finally {
    recognizer?.close();
  }

  // 4. 使用Claude处理文本
  const processedContent = await processWithClaude([
    { role: 'user', content: `请处理以下播客内容：\n${transcription}` }
  ]);

  // 5. 生成结构化数据
  return {
    originalUrl: episodeUrl,
    transcription: transcription,
    summary: processedContent.summary,
    keyPoints: processedContent.key_points,
    timestamp: new Date().toISOString()
  };
  }
}

module.exports = PodcastProcessor;
