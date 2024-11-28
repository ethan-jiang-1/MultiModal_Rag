from dotenv import load_dotenv
import os
import sys
#import logging
import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.gen_lp.gen_markdown_llamaparse import generate_markdown_llamaparse

def gen_md_llamaparse(doc_pathname, out_dir):
    #logging.info(parser)

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine("llamaparse:lp")
    md_info.set_doc_pathname(doc_pathname)

    generate_markdown_llamaparse(doc_pathname)
    
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)