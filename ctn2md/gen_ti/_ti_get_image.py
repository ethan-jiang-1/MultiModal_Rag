
import sys
import logging

import time
import httpx  # 添加到文件顶部的 imports

if './' not in sys.path:
    sys.path.append("./")


def download_remote_image_ti(img_url: str, local_path: str) -> bool:
    max_retries = 3
    with httpx.Client() as client:
        for attempt in range(max_retries):
            try:
                response = client.get(img_url, timeout=10.0)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
            except (httpx.RequestError, httpx.HTTPStatusError, IOError) as e:
                if attempt == max_retries - 1:
                    raise
                delay = (attempt + 1) * 1
                logging.warning(f"Download attempt {attempt + 1} failed for {img_url}. Retrying in {delay}s... Error: {str(e)}")
                time.sleep(delay)
    return False