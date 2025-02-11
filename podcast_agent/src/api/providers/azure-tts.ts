import { BaseProvider } from '../transform/stream';
import axios from 'axios';
import LRU from 'lru-cache';

export class AzureTTSProvider extends BaseProvider {
  private cache = new LRU<string, Buffer>({
    max: 100,
    ttl: 1000 * 60 * 60 * 24 // 24小时缓存
  });

  async synthesize(text: string): Promise<Buffer> {
    const cacheKey = this.hashText(text);
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const endpoint = `https://${process.env.AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`;
    const response = await axios.post(endpoint, this.buildSSML(text), {
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.AZURE_TTS_KEY!,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3'
      },
      responseType: 'arraybuffer'
    });

    const audioBuffer = Buffer.from(response.data);
    this.cache.set(cacheKey, audioBuffer);
    return audioBuffer;
  }

  private buildSSML(text: string): string {
    return `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">
      <voice name="zh-CN-XiaoxiaoNeural">
        <prosody rate="+10%" pitch="+5Hz">${text}</prosody>
      </voice>
    </speak>`;
  }

  private hashText(text: string): string {
    return require('crypto').createHash('sha256').update(text).digest('hex');
  }
}
