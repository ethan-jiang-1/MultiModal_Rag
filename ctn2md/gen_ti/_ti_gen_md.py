import sys
import os
from dotenv import load_dotenv
import httpx
import json
import logging
import rich
#import time
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
#from typing import Union

load_dotenv()
if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers


class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'
        self.max_retries = 3
        self._headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }

    @staticmethod
    def _get_file_content(filePath: str) -> bytes:
        """提取公共的文件读取函数"""
        with open(filePath, 'rb') as fp:
            return fp.read()

    @staticmethod
    def _get_default_options() -> dict:
        """提取公共的选项配置"""
        return {
            'page_start': 0,
            'page_count': 1000,
            'table_flavor': 'md',
            'parse_mode': 'scan',
            'page_details': 0,
            'markdown_details': 1,
            'apply_document_tree': 1,
            'dpi': 144
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def recognize_pdf2md(self, image: bytes, options: dict = None) -> httpx.Response:
        """同步方法，添加重试机制"""
        options = options or self._get_default_options()
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        try:
            with httpx.Client() as client:
                try:
                    response = client.post(
                        url,
                        content=image,
                        headers=self._headers, 
                        params=options, 
                        timeout=30.0
                    )
                    response.raise_for_status()
                    return response
                except Exception as e:
                    retry_state = getattr(self.recognize_pdf2md, 'retry_state', None)
                    if retry_state and retry_state.attempt_number < 3:
                        logging.warning(f"Attempt {retry_state.attempt_number}/3: PDF to Markdown conversion failed: {str(e)}")
                    else:
                        logging.exception("Final attempt for PDF to Markdown conversion failed")
                    raise
        except Exception as e:
            retry_state = getattr(self.recognize_pdf2md, 'retry_state', None)
            if retry_state and retry_state.attempt_number < 3:
                logging.warning(f"Attempt {retry_state.attempt_number}/3: Error in recognize_pdf2md: {str(e)}")
            else:
                logging.exception("Final attempt failed in recognize_pdf2md")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def recognize_pdf2md_async(self, image: bytes, options: dict = None) -> httpx.Response:
        """异步方法，添加重试机制"""
        options = options or self._get_default_options()
        url = self.host + '/ai/service/v1/pdf_to_markdown'

        try:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        url, 
                        content=image, 
                        headers=self._headers, 
                        params=options, 
                        timeout=30.0
                    )
                    response.raise_for_status()
                    return response
                except Exception as e:
                    retry_state = getattr(self.recognize_pdf2md_async, 'retry_state', None)
                    if retry_state and retry_state.attempt_number < 3:
                        logging.warning(f"Attempt {retry_state.attempt_number}/3: PDF to Markdown conversion failed: {str(e)}")
                    else:
                        logging.exception("Final attempt for PDF to Markdown conversion failed")
                    raise
        except Exception as e:
            retry_state = getattr(self.recognize_pdf2md_async, 'retry_state', None)
            if retry_state and retry_state.attempt_number < 3:
                logging.warning(f"Attempt {retry_state.attempt_number}/3: Error in recognize_pdf2md_async: {str(e)}")
            else:
                logging.exception("Final attempt failed in recognize_pdf2md_async")
            raise


def convert_image_to_md(pname_image: str) -> str:
    """同步转换函数"""
    x_ti_app_id = os.getenv('X_TI_APP_ID')
    x_ti_secret_code = os.getenv('X_TI_SECRET_CODE')
    textin = TextinOcr(x_ti_app_id, x_ti_secret_code)

    image = textin._get_file_content(pname_image)
    
    logging.info(f"CIM: requesting {pname_image} to textin")
    resp = textin.recognize_pdf2md(image)  # 使用默认选项
    logging.info(f"CIM: request time: {resp.elapsed.total_seconds()} from textin")

    result = json.loads(resp.text)
    return result['result']['markdown']


async def convert_image_to_md_async(pname_image: str) -> str:
    """异步转换函数"""
    x_ti_app_id = os.getenv('X_TI_APP_ID')
    x_ti_secret_code = os.getenv('X_TI_SECRET_CODE')
    textin = TextinOcr(x_ti_app_id, x_ti_secret_code)

    image = textin._get_file_content(pname_image)

    logging.info(f"CIMA: requesting {pname_image} to textin")
    resp = await textin.recognize_pdf2md_async(image)  # 使用默认选项
    logging.info(f"CIMA: request time: {resp.elapsed.total_seconds()} from textin")

    result = json.loads(resp.text)
    return result['result']['markdown']


if __name__ == "__main__":
    setup_logger_handlers()
    
    pname_image = "_work/md_pdf_pages/5ec48698-page_1.jpg"
    
    # 同步测试
    result_sync = convert_image_to_md(pname_image)
    rich.print("[Sync] Result:", result_sync[:100] + "...")

    # 异步测试
    async def test_async():
        result_async = await convert_image_to_md_async(pname_image)
        rich.print("[Async] Result:", result_async[:100] + "...")

    asyncio.run(test_async())
