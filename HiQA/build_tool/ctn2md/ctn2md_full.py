from dotenv import load_dotenv
import os
import sys
#import logging
import rich
import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
#from HiQA.build_tool.ctn2md.ctn2md_base import save_md_info
from HiQA.build_tool.ctn2md.ctn2md_llamaparse_converter import convert_doc_to_md_by_llamaparse
from HiQA.build_tool.ctn2md.ctn2md_ocr_fixer import fix_ocr_content_by_gpt
from HiQA.build_tool.ctn2md.ctn2md_img_ref_fixer import fix_img_content_by_lvlm

def do_content2md_convert(ctn_pathname, out_dir):
    md_info_path, md_info = convert_doc_to_md_by_llamaparse(ctn_pathname, out_dir)
    md_info_path, md_info = fix_ocr_content_by_gpt(md_info_path)
    md_info_path, md_info = fix_img_content_by_lvlm(md_info_path)
    return md_info_path, md_info

if __name__ == "__main__":
    doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"

    out_dir = f"_work/cnt2md_{random.randint(10,99)}"
    print(f"out_dir: {out_dir}")

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path, md_info = do_content2md_convert(doc_pathname, out_dir)
    print(md_info_path)
    rich.print(md_info)