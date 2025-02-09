import logging
import time
from pathlib import Path
from typing import Dict, List
import feedparser
from .audio_processor import AudioProcessor

class PodcastAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.audio_processor = AudioProcessor(config)
        self._init_directories()

    def _init_directories(self):
        """初始化所需目录结构"""
        Path(self.config['model_paths']['vosk']).mkdir(parents=True, exist_ok=True)
        Path(self.config['storage']['output_dir']).mkdir(parents=True, exist_ok=True)

    def process_feeds(self, feeds: List[Dict]):
        """处理所有订阅源"""
        for feed in feeds:
            try:
                logger.info(f"开始处理订阅源: {feed['url']}")
                episodes = self._fetch_feed(feed['url'])
                self._process_episodes(episodes, feed['category'])
            except Exception as e:
                logger.error(f"处理订阅源失败: {feed['url']} - {str(e)}")

    def _fetch_feed(self, url: str) -> List[Dict]:
        """获取并解析RSS订阅内容"""
        try:
            feed = feedparser.parse(url)
            return [{
                'title': entry.title,
                'url': entry.enclosures[0].href,
                'published': entry.published_parsed
            } for entry in feed.entries]
        except Exception as e:
            logger.error(f"RSS解析失败: {url} - {str(e)}")
            return []

    def _process_episodes(self, episodes: List[Dict], category: str):
        """处理单播客的所有剧集"""
        for episode in episodes:
            try:
                if self._should_process(episode):
                    self._process_single_episode(episode, category)
            except Exception as e:
                logger.error(f"处理剧集失败: {episode['title']} - {str(e)}")

    def _should_process(self, episode: Dict) -> bool:
        """判断是否需要处理该剧集"""
        # 实现去重逻辑（需根据实际存储方案实现）
        return True

    def _process_single_episode(self, episode: Dict, category: str):
        """处理单个播客剧集"""
        start_time = time.time()

        # 下载音频
        audio_path = Path(self.config['storage']['output_dir']) / f"{category}_{episode['title']}.mp3"
        if self.audio_processor.download_audio(episode['url'], audio_path):
            # 语音转写
            transcript = self.audio_processor.transcribe_audio(audio_path)

            if transcript:
                # 文本处理
                processed_text = self.audio_processor.process_text(transcript)

                # 保存处理结果
                self._save_processing_result(
                    audio_path=audio_path,
                    transcript=transcript,
                    processed_text=processed_text,
                    metadata=episode
                )

        logger.info(f"处理完成: {episode['title']} - 耗时: {time.time()-start_time:.2f}s")

    def _save_processing_result(self, **kwargs):
        """保存处理结果（需实现具体存储逻辑）"""
        # 示例：保存到JSON文件
        output_path = Path(self.config['storage']['output_dir']) / f"{kwargs['metadata']['title']}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kwargs, f, ensure_ascii=False, indent=2)

def main(config_path: str = "config.yaml"):
    """程序主入口"""
    # 加载配置
    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化代理
    agent = PodcastAgent(config)

    # 处理订阅源
    agent.process_feeds(config['feeds'])

if __name__ == "__main__":
    main()
