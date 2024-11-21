from dotenv import load_dotenv
import os
import sys
import logging
import rich
import random
#import json
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import MdInfo
from HiQA.build_tool.ctn2md.ctn2md_llamaparse_md_generater import gen_md_llamaparse
from HiQA.build_tool.ctn2md.ctn2md_fix_heading_llamaparse import fix_headings_llamaparse
from HiQA.build_tool.ctn2md.ctn2md_fix_content_ocr import fix_ocr_content_by_gpt
from HiQA.build_tool.ctn2md.ctn2md_fix_img_reference import fix_img_reference_by_lvlm
from HiQA.build_tool.ctn2md.ctn2md_fix_heading_hiqa import fix_headings_for_hiqa


def make_final_md(md_info_path):
    md_info = MdInfo(md_info_path)
    last_step_num = md_info.get_last_step_num()
    pathname_step_md = md_info.name_step_pathname(last_step_num)
    pathname_final_md = md_info.name_step_pathname(-1)

    if os.path.isfile(pathname_final_md):
        os.unlink(pathname_final_md)
    shutil.copy(pathname_step_md, pathname_final_md)

    md_info["fname_final_md"] = os.path.basename(pathname_final_md)
    md_info.save()
    return pathname_final_md

def do_content2md_convert(ctn_pathname, out_dir):
    md_info_path = gen_md_llamaparse(ctn_pathname, out_dir)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @convert_doc_to_md_by_llamaparse")
        return None, None 

    md_info_path = fix_headings_llamaparse(md_info_path, src_step_num=0)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_headings_llamaparse")
        return None, None 

    md_info_path = fix_ocr_content_by_gpt(md_info_path, src_step_num=1)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_ocr_content_by_gpt")
        return None, None 

    md_info_path = fix_img_reference_by_lvlm(md_info_path, src_step_num=2)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_img_reference_by_lvlm")
        return None, None 

    md_info_path = fix_headings_for_hiqa(md_info_path, src_step_num=3)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_headings_for_hiqa")
        return None, None 

    final_md_path = make_final_md(md_info_path)

    return final_md_path

if __name__ == "__main__":
    setup_logger_handlers()
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/Long-Context LLMs Meet RAG_compressed.pdf"

    out_dir = f"_work/ctn2md_{random.randint(10,99)}"
    print(f"out_dir: {out_dir}")

    os.makedirs(out_dir, exist_ok=True)
    final_md_path = do_content2md_convert(doc_pathname, out_dir)
    print(final_md_path)

    md_info = MdInfo(final_md_path)
    rich.print(md_info)
    print(final_md_path)