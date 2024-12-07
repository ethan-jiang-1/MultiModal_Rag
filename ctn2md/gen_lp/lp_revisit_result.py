from dotenv import load_dotenv
#import os
import sys
#import logging
import rich
#import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_ctn_type import CTN_TYPE # noqa
from ctn2md.src.md_info_base import MdInfo, MIFN  # noqa


# MAX_OUTPUT_TOKEN = 8*1024

# def _calculate_tokens_large_text(text, chunk_size=2048, stop_check_over_max=False):
#     from ctn2md.utils.util_tokenizer import get_token_encoding
#     """
#     针对超长文本的 Token 数量计算，分块处理。
    
#     :param text: 输入的长字符串
#     :param chunk_size: 每块的最大字符数
#     :param encoding_name: 编码器名称
#     :return: Token 数量
#     """
#     # 获取编码器
#     encoding = get_token_encoding()
    
#     # 初始化 Token 计数器
#     total_tokens = 0
    
#     # 分块处理
#     for i in range(0, len(text), chunk_size):
#         chunk = text[i:i + chunk_size]
#         tokens = encoding.encode(chunk)
#         total_tokens += len(tokens)

#         if total_tokens > MAX_OUTPUT_TOKEN:
#             return total_tokens
    
#     return total_tokens

def _assign_ctn_type(md_info, json_result):
    doc_type = md_info.get_doc_type()
    md_info[MIFN.CTN_TYPE] = CTN_TYPE.get_ctn_type_by_doc_type(doc_type)
    if json_result is not None and len(json_result) > 0:
        json_result0_pages = json_result[0].get("pages", None)
        if json_result0_pages is not None and len(json_result0_pages) > 0:
            page1 = json_result0_pages[0]
            if page1["page"] == 1:
                page_width = page1["width"]
                page_height = page1["height"]
                if md_info[MIFN.CTN_TYPE] == CTN_TYPE.PDF:
                    if page_width > page_height:
                        md_info[MIFN.CTN_TYPE] = CTN_TYPE.PPT
        md_info.save()

def post_scan_llamaparse_result(md_info, json_result=None):
    _assign_ctn_type(md_info, json_result)


if __name__ == "__main__":
    
    md_info_path = "_output/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    md_info = MdInfo(md_info_path)

    ret = post_scan_llamaparse_result(md_info)
    rich.print(ret)