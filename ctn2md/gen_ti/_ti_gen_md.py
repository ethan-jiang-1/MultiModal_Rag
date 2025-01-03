import sys
import os
from dotenv import load_dotenv
import httpx
import json
import logging
import rich
import time


if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers

load_dotenv()



class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image: bytes, options: dict) -> httpx.Response:
        """
        pdf to markdown
        :param options: request params
        :param image: file bytes
        :return: response

        options = {
            'pdf_pwd': None,
            'dpi': 144,  # 设置dpi为144
            'page_start': 0,
            'page_count': 1000,  # 设置解析的页数为1000页
            'apply_document_tree': 0,
            'markdown_details': 1,
            'page_details': 0,  # 不包含页面细节信息
            'table_flavor': 'md',
            'get_image': 'none',
            'parse_mode': 'scan',  # 解析模式设为scan
        }
        """
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }
        max_retries = 3
        with httpx.Client() as client:
            for attempt in range(max_retries):
                try:
                    response = client.post(url, content=image, headers=headers, params=options, timeout=30.0)
                    response.raise_for_status()
                    return response
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise  # Re-raise the last exception if all retries failed
                    
                    delay = (attempt + 1) * 1
                    logging.warning(f"Request attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
                    time.sleep(delay)


def convert_image_to_md(pname_image: str) -> str:
    x_ti_app_id = os.getenv('X_TI_APP_ID')
    x_ti_secret_code = os.getenv('X_TI_SECRET_CODE')
    textin = TextinOcr(x_ti_app_id, x_ti_secret_code)

    def _get_file_content(filePath: str) -> bytes:
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = _get_file_content(pname_image)

    logging.info(f"CIM: requesting {pname_image} to textin")
    resp = textin.recognize_pdf2md(image, {
        'page_start': 0,
        'page_count': 1000,  # 设置解析页数为1000页
        'table_flavor': 'md',
        'parse_mode': 'scan',  # 设置解析模式为scan模式
        'page_details': 0,  # 不包含页面细节
        'markdown_details': 1,
        'apply_document_tree': 1,
        'dpi': 144  # 分辨率设置为144 dpi
    })
    logging.info(f"CIM: request time: {resp.elapsed.total_seconds()} from textin")

    result = json.loads(resp.text)
    # with open(f'_work/testin/result_{os.path.basename(pname_image)}.json', 'w', encoding='utf-8') as fw:
    #     json.dump(result, fw, indent=4, ensure_ascii=False)

    return result['result']['markdown']


if __name__ == "__main__":
    setup_logger_handlers() 
    
    pname_image = "_work/md_pdf_pages/5ec48698-page_1.jpg"
    result = convert_image_to_md(pname_image)
    rich.print(result)
