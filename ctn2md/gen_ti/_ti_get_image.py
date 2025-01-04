import sys
import logging
import time
import asyncio
import httpx
from pathlib import Path

if './' not in sys.path:
    sys.path.append("./")


class ImageDownloader:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def download_image(self, img_url: str, local_path: str) -> bool:
        """同步下载图片"""
        with httpx.Client() as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.get(img_url, timeout=10.0)
                    response.raise_for_status()
                    with open(local_path, 'wb') as f:
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
        """异步下载图片"""
        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(img_url, timeout=10.0)
                    response.raise_for_status()
                    # 确保目标目录存在
                    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(local_path, 'wb') as f:
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
def download_remote_image_ti(img_url: str, local_path: str) -> bool:
    """保持原有函数接口的同步下载方法"""
    downloader = ImageDownloader()
    return downloader.download_image(img_url, local_path)


async def download_remote_image_ti_async(img_url: str, local_path: str) -> bool:
    """新增的异步下载方法"""
    downloader = ImageDownloader()
    return await downloader.download_image_async(img_url, local_path)


if __name__ == "__main__":
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试URL和本地路径
    test_url = "https://img.ixintu.com/download/jpg/20210201/7cacc87485bdd0b5c721c7c100f67550_512_512.jpg!ys"
    test_path_sync = "_work/test_download_sync.jpg"
    test_path_async = "_work/test_download_async.jpg"

    # 同步测试
    print("\n=== Testing Synchronous Download ===")
    try:
        result = download_remote_image_ti(test_url, test_path_sync)
        print(f"Sync download {'successful' if result else 'failed'}")
        print(f"File exists: {Path(test_path_sync).exists()}")
    except Exception as e:
        print(f"Sync download error: {e}")

    # 异步测试
    print("\n=== Testing Asynchronous Download ===")

    async def test_async():
        try:
            result = await download_remote_image_ti_async(test_url, test_path_async)
            print(f"Async download {'successful' if result else 'failed'}")
            print(f"File exists: {Path(test_path_async).exists()}")
        except Exception as e:
            print(f"Async download error: {e}")

    asyncio.run(test_async())