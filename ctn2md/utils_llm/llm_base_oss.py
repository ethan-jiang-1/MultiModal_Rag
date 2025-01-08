import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

from dotenv import load_dotenv
import os
import logging
import rich
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_none,
)

load_dotenv()

from ctn2md.utils.util_logging import setup_logger_handlers

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

def _generate_unique_name(image_path: str) -> str:
    # 获取当前日期并格式化为年月路径
    date_prefix = datetime.now().strftime('%Y%m')
    
    # 从原始文件名生成唯一名称
    base_name = os.path.basename(image_path)
    
    # 组合路径：年月/文件名
    object_name = f"{date_prefix}/{base_name}"
    return object_name

def _upload_image_to_oss_core(object_name: str, image_path:str) -> str:
    import oss2
    
    access_key_id = os.environ["OSS_ACCESS_KEY_ID"]
    access_key_secret = os.environ["OSS_ACCESS_KEY_SECRET"]
    endpoint = os.environ["OSS_ENDPOINT"]
    bucket_name = os.environ["OSS_BUCKET_NAME"]

    try:
        # 初始化OSS存储
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 检查对象是否已存在
        if not bucket.object_exists(object_name):
            logging.info(f"Uploading {image_path} to oss as {object_name}")
            headers = {
                'Content-Disposition': 'inline',
                'x-oss-object-acl': oss2.OBJECT_ACL_PUBLIC_READ
            }
            with open(image_path, 'rb') as file:
                result = bucket.put_object(object_name, file, headers=headers)
            
            # 验证上传结果
            if result.status != 200:
                raise Exception(f"Upload failed with status {result.status}")
        else:
            # 获取已存在文件的信息
            result = bucket.head_object(object_name)
            if result.status != 200:
                raise Exception(f"Head object failed with status {result.status}")

        # 验证文件确实存在且可访问
        meta = bucket.get_object_meta(object_name)
        if meta.status != 200:
            raise Exception(f"Cannot access uploaded file, status: {meta.status}")

        # 获取基础URL并验证可访问性
        base_url = bucket.sign_url('GET', object_name, 0).split('?')[0]
        
        # 使用 httpx 验证URL可访问性
        with httpx.Client() as client:
            response = client.head(base_url, timeout=10.0)
            response.raise_for_status()
            
        # 构建带ETag的URL
        final_url = f"{base_url}?ETag={result.etag}"
        logging.info(f"public url with ETag:{final_url} to access {object_name} in oss")
        
        return final_url

    except (oss2.exceptions.OssError, httpx.RequestError) as e:
        logging.error(f"OSS operation failed for {object_name}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error during OSS operation for {object_name}: {str(e)}")
        raise

def get_retry_wait(retry_state):
    """根据环境返回重试等待策略"""
    if os.environ.get('PYTEST_CURRENT_TEST'):
        return wait_none()(retry_state)
    return wait_exponential(multiplier=1, min=4, max=10)(retry_state)

def validate_image_file_type(image_path: str) -> None:
    """验证图片文件类型是否支持"""
    if not os.path.splitext(image_path)[1].lower() in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {image_path}")

@retry(stop=stop_after_attempt(3), wait=get_retry_wait)
def upload_image_to_oss(image_path:str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    validate_image_file_type(image_path)

    # 生成带日期路径的对象名
    object_name = _generate_unique_name(image_path)
    final_url = _upload_image_to_oss_core(object_name, image_path)
    return final_url
    

if __name__ == "__main__":
    setup_logger_handlers()
    
    image_path = "_work/md_pdf_pages/b545fabd-page_2.jpg"
    url = upload_image_to_oss(image_path)
    rich.print(url)
