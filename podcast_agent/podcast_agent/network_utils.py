import aiohttp
import hashlib
from pathlib import Path
import asyncio
from typing import Optional
from .schemas import PodcastEpisode

CACHE_DIR = Path("podcast_cache")
CACHE_DIR.mkdir(exist_ok=True)

async def download_episode(episode: PodcastEpisode, max_retries: int = 3) -> Optional[Path]:
    """异步下载播客音频文件并缓存"""
    file_hash = hashlib.sha256(episode.episode_url.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{file_hash}.{episode.audio_format}"

    if cache_path.exists():
        return cache_path

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=episode.max_duration)) as session:
        for attempt in range(max_retries):
            try:
                async with session.get(episode.episode_url) as response:
                    if response.status == 200:
                        with open(cache_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024*1024):
                                f.write(chunk)
                        return cache_path
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to download after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)

    return None
