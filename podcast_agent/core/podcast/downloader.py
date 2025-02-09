import aiohttp
import asyncio
from datetime import datetime
from pathlib import Path
import logging
from .exceptions import PodcastError

class PodcastDownloader:
    def __init__(self, max_retries=3, timeout=30):
        self.max_retries = max_retries
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.logger = logging.getLogger(__name__)

    async def download(self, url, output_dir="downloads"):
        """异步下载播客文件并保存到指定目录"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"podcast_{datetime.now().strftime('%Y%m%d%H%M%S')}{Path(url).suffix}"
        filepath = Path(output_dir) / filename

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for attempt in range(self.max_retries):
                try:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        with open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024*1024):
                                f.write(chunk)
                        self.logger.info(f"成功下载文件到: {filepath}")
                        return str(filepath)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == self.max_retries - 1:
                        raise PodcastError(f"下载失败: {str(e)}") from e
                    await asyncio.sleep(2**attempt)

    async def batch_download(self, urls, output_dir="downloads"):
        """批量下载多个播客文件"""
        tasks = [self.download(url, output_dir) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
