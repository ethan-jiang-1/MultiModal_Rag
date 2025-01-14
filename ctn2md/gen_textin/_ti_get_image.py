import logging
import time
import asyncio
import httpx
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv
import shutil

load_dotenv()
from ctn2md.md_info.md_info_base import MdInfo


class ImageDownloader:
    def __init__(self, md_info: MdInfo, max_retries: int = 3, timeout: int = 10):
        self.md_info = md_info
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_dir = md_info.get_cache_dir()
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, img_url: str) -> str:
        """计算图片URL的缓存路径"""
        url_hash = hashlib.sha1(img_url.encode()).hexdigest()[:16]
        ext = Path(img_url).suffix or '.jpg'
        cache_name = f"img_{url_hash}{ext}"
        return str(Path(self.cache_dir) / cache_name)

    def download_image(self, img_url: str, local_path: str) -> bool:
        """同步下载图片,使用缓存"""
        cache_path = self._get_cache_path(img_url)
        
        # 检查缓存
        if Path(cache_path).exists():
            shutil.copy2(cache_path, local_path)
            return True

        # 下载新图片
        with httpx.Client() as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.get(img_url, timeout=self.timeout)
                    response.raise_for_status()
                    
                    # 保存到缓存和目标位置
                    for path in [cache_path, local_path]:
                        Path(path).parent.mkdir(parents=True, exist_ok=True)
                        with open(path, 'wb') as f:
                            f.write(response.content)
                    return True
                except (httpx.RequestError, httpx.HTTPStatusError, IOError) as e:
                    if attempt == self.max_retries - 1:
                        raise
                    delay = (attempt + 1) * 1
                    logging.warning(f"Download attempt {attempt + 1} failed for {img_url}. Retrying in {delay}s... Error: {str(e)}")
                    time.sleep(delay)
        return False

    async def download_image_async(self, img_url: str, local_path: str) -> bool:
        """异步下载图片,使用缓存"""
        cache_path = self._get_cache_path(img_url)
        
        # 检查缓存
        if Path(cache_path).exists():
            shutil.copy2(cache_path, local_path)
            return True

        # 下载新图片
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(img_url, timeout=self.timeout)
                    response.raise_for_status()
                    
                    # 保存到缓存和目标位置
                    for path in [cache_path, local_path]:
                        Path(path).parent.mkdir(parents=True, exist_ok=True)
                        with open(path, 'wb') as f:
                            f.write(response.content)
                    return True
                except (httpx.RequestError, httpx.HTTPStatusError, IOError) as e:
                    if attempt == self.max_retries - 1:
                        raise
                    delay = (attempt + 1) * 1
                    logging.warning(f"Download attempt {attempt + 1} failed for {img_url}. Retrying in {delay}s... Error: {str(e)}")
                    await asyncio.sleep(delay)
        return False


# 为了保持向后兼容，保留原有的函数接口
def download_remote_image_ti(md_info: MdInfo, img_url: str, local_path: str) -> bool:
    """保持原有函数接口的同步下载方法"""
    downloader = ImageDownloader(md_info)
    return downloader.download_image(img_url, local_path)


async def download_remote_image_ti_async(md_info: MdInfo, img_url: str, local_path: str) -> bool:
    """新增的异步下载方法"""
    downloader = ImageDownloader(md_info)
    return await downloader.download_image_async(img_url, local_path)


if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()


    class TestMdInfo:
        def __getitem__(self, key):
            return None
        
        def get_unique_job_id(self):
            return "test_job"
        
        def get_out_dir(self):
            return "_work/test_output"
        
        def get_md_control(self, key, default):
            return default
        
        def get_doc_title(self):
            return "Test Document"

        def get_cache_dir(self):
            cache_dir = "_work/test_cache"
            os.makedirs(cache_dir, exist_ok=True)
            return cache_dir
        
    md_info = TestMdInfo()

    # 测试URL和本地路径
    test_url = "https://img.ixintu.com/download/jpg/20210201/7cacc87485bdd0b5c721c7c100f67550_512_512.jpg!ys"
    test_path_sync = "_work/test_download_sync.jpg"
    test_path_async = "_work/test_download_async.jpg"

    # 同步测试
    print("\n=== Testing Synchronous Download ===")
    try:
        result = download_remote_image_ti(md_info, test_url, test_path_sync)
        print(f"Sync download {'successful' if result else 'failed'}")
        print(f"File exists: {Path(test_path_sync).exists()}")
    except Exception as e:
        print(f"Sync download error: {e}")

    # 异步测试
    print("\n=== Testing Asynchronous Download ===")

    async def test_async():
        try:
            result = await download_remote_image_ti_async(md_info, test_url, test_path_async)
            print(f"Async download {'successful' if result else 'failed'}")
            print(f"File exists: {Path(test_path_async).exists()}")
        except Exception as e:
            print(f"Async download error: {e}")

    asyncio.run(test_async())