from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.ctn2md_base import save_md_info

def fix_img_content_by_mm(fname_output_s1_md, out_dir, md_info):
    fname_s2_md_name = os.path.basename(fname_output_s1_md).replace("_s1.md", "_s2.md")
    fname_output_s2_md = os.path.join(out_dir, fname_s2_md_name)

    with open(fname_output_s1_md, "r", encoding="utf8") as f:
        md_text = f.read()
        rich.print(md_text)

    # md_text_fixed = fix_ocr_self_correct_markdown(md_text)
    # with open(fname_output_s1_md, "w+") as f:
    #     f.write(md_text_fixed)

    logging.info(f"fname_s2_md_name: {fname_s2_md_name}")
    if isinstance(md_info, dict):
        md_info["fname_s2_md_name"] = os.path.basename(fname_s2_md_name)
        save_md_info(out_dir, md_info)
    return fname_output_s2_md    


# def full_process_doc2md(doc_pathname, out_dir):
#     fname_output_s0_md, md_info = convert_doc_to_md_by_llamaparse(doc_pathname, out_dir)
#     fname_output_s1_md = fix_ocr_content_by_gpt(fname_output_s0_md, out_dir, md_info)
#     fname_output_s2_md = fix_img_content_by_mm(fname_output_s1_md, out_dir, md_info)

#     save_md_info(out_dir, md_info)

if __name__ == "__main__":
    setup_logger_handlers()
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    # doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"

    # out_dir = f"_work/lp_doc2md_{random.randint(10,99)}"
    # print(f"out_dir: {out_dir}")

    # setup_logger_handlers()
    # os.makedirs(out_dir, exist_ok=True)
    # fname_output_fixed_md, md_info = convert_doc_to_md_by_llamaparse(doc_pathname, out_dir)
    # print(fname_output_fixed_md)
    # rich.print(md_info)