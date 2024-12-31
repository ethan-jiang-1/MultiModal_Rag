import requests
import json
import os
from dotenv import load_dotenv
import rich

load_dotenv()
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image, options):
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

        return requests.post(url, data=image, headers=headers, params=options)


def main(pname_image):
    # 请登录后前往 “工作台-账号设置-开发者信息” 查看 app-id/app-secret
    x_ti_app_id = os.getenv('X_TI_APP_ID')
    x_ti_secret_code = os.getenv('X_TI_SECRET_CODE')
    textin = TextinOcr(x_ti_app_id, x_ti_secret_code)

    image = get_file_content(pname_image)

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
    print("request time: ", resp.elapsed.total_seconds())

    result = json.loads(resp.text)
    with open(f'_work/testin/result_{os.path.basename(pname_image)}.json', 'w', encoding='utf-8') as fw:
        json.dump(result, fw, indent=4, ensure_ascii=False)

    return result['result']['markdown']

if __name__ == "__main__":
    pname_image_file = "_work/md_pdf_pages/5ec48698-page_1.jpg"
    ret = main(pname_image_file)
    rich.print(ret)


