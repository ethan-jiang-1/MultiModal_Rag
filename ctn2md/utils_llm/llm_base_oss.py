from dotenv import load_dotenv
import sys
import os
import logging
import rich
from datetime import datetime


if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

def _generate_unique_name(image_path: str) -> str:
    # 获取当前日期并格式化为年月路径
    date_prefix = datetime.now().strftime('%Y%m')
    
    # 从原始文件名生成唯一名称
    base_name = os.path.basename(image_path)
    
    # 组合路径：年月/文件名_时间戳
    object_name = f"{date_prefix}/{base_name}"
    return object_name


def upload_image_to_oss(image_path:str) -> str:
    import oss2
    access_key_id = os.environ["OSS_ACCESS_KEY_ID"]
    access_key_secret = os.environ["OSS_ACCESS_KEY_SECRET"]
    endpoint = os.environ["OSS_ENDPOINT"]
    bucket_name = os.environ["OSS_BUCKET_NAME"]

    # 初始化OSS存储
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    # 生成带日期路径的对象名
    object_name = _generate_unique_name(image_path)
    
    # 检查对象是否已存在
    if not bucket.object_exists(object_name):
        logging.info(f"Uploading {image_path} to oss as {object_name}")
        headers = {
            'Content-Disposition': 'inline',
            'x-oss-object-acl': oss2.OBJECT_ACL_PUBLIC_READ
        }
        with open(image_path, 'rb') as file:
            result = bucket.put_object(object_name, file, headers=headers)
    else:
        # 获取已存在文件的信息
        result = bucket.head_object(object_name)

    # 获取基础URL
    base_url = bucket.sign_url('GET', object_name, 0).split('?')[0]
        
    # 构建带ETag和过期时间的URL
    final_url = f"{base_url}?ETag={result.etag}"
    logging.info(f"public url with ETag:{final_url} to access {object_name} in oss")
    
    return final_url

if __name__ == "__main__":
    image_path = "_work/md_pdf_pages/b545fabd-page_2.jpg"
    url = upload_image_to_oss(image_path)
    rich.print(url)
