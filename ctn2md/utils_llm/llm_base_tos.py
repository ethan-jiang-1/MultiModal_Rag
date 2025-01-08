from dotenv import load_dotenv
import os
import logging
import httpx
from datetime import datetime
import tos
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

def _generate_unique_name(image_path: str) -> str:
    """提取公共的文件读取函数"""
    date_prefix = datetime.now().strftime('%Y%m')
    base_name = os.path.basename(image_path)
    object_name = f"{date_prefix}/{base_name}"
    return object_name

def _upload_image_to_tos_core(object_name: str, image_path: str) -> str:
    """上传图片到火山引擎TOS的核心逻辑

    Args:
        object_name: TOS中的对象名称
        image_path: 本地图片路径
    
    Returns:
        str: 图片的公开访问URL
        
    Raises:
        Exception: 上传失败时抛出异常
    """
    access_key = os.environ["VOLC_ACCESSKEY"]
    secret_key = os.environ["VOLC_SECRETKEY"]
    endpoint = os.environ["VOLC_ENDPOINT"].replace("https://", "")  # 移除https://前缀
    region = endpoint.split('.')[0].split('-', 1)[1]  # 从endpoint提取region，如"cn-beijing"
    bucket_name = os.environ["VOLC_BUCKET_NAME"]
    
    try:
        # 初始化TOS客户端
        client = tos.TosClient(
            tos.Auth(access_key, secret_key, region),
            endpoint
        )
        
        # 上传文件
        logging.info(f"Uploading {image_path} to tos as {object_name}")
        with open(image_path, 'rb') as file:
            result = client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=file
            )
            
            if not result or not hasattr(result, 'etag'):
                raise Exception("Upload failed: no ETag returned")
                
        # 构建访问URL（根据火山引擎TOS的URL格式）
        base_url = f"https://{bucket_name}.{endpoint}/{object_name}"
        
        # 验证URL可访问性
        with httpx.Client() as client:
            response = client.head(base_url, timeout=10.0)
            response.raise_for_status()
            
        logging.info(f"Successfully uploaded to TOS: {base_url}")
        return base_url
        
    except Exception as e:
        logging.error(f"TOS operation failed for {object_name}: {str(e)}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def upload_image_to_tos(image_path: str) -> str:
    """上传图片到火山引擎TOS并返回可访问的URL

    Args:
        image_path: 本地图片路径
    
    Returns:
        str: 图片的公开访问URL
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        ValueError: 文件类型不支持时抛出
        Exception: 其他上传失败情况
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if not os.path.splitext(image_path)[1].lower() in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {image_path}")
    
    # 生成带日期路径的对象名
    object_name = _generate_unique_name(image_path)
    return _upload_image_to_tos_core(object_name, image_path)

if __name__ == "__main__":
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试上传
    image_path = "_work/md_pdf_pages/b545fabd-page_2.jpg"
    
    print("\n=== Testing TOS Upload ===")
    try:
        url = upload_image_to_tos(image_path)
        print(f"TOS Upload successful. URL: {url}")
    except Exception as e:
        print(f"TOS Upload error: {e}") 