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
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info, find_md_info_path
from HiQA.build_tool.ctn2md.ctn2md_md_generater import cnt2md_generator
from HiQA.build_tool.ctn2md.ctn2md_ocr_fixer import fix_ocr_content_by_gpt
from HiQA.build_tool.ctn2md.ctn2md_img_ref_fixer import fix_img_content_by_lvlm
from HiQA.build_tool.ctn2md.ctn2md_heading_md_fixer import fix_markdown_headings
from HiQA.build_tool.ctn2md.ctn2md_hiqa_md_fixer import fix_markdown_content_for_hiqa


def make_final_md(md_info_path, md_info):
    fname_output_s3_md = md_info.get("fname_output_s3_md")
    fname_output_md = fname_output_s3_md.replace("_s3.md", ".md")

    src_path = os.path.join(out_dir, fname_output_s3_md)
    final_md_path = os.path.join(out_dir, fname_output_md)
    if os.path.isfile(final_md_path):
        os.unlink(final_md_path)
    shutil.copy(src_path, final_md_path)

    md_info["fname_final_md"] = os.path.basename(final_md_path)
    save_md_info(out_dir, md_info)
    return final_md_path

def do_content2md_convert(ctn_pathname, out_dir):
    output_md_path, md_info = cnt2md_generator(ctn_pathname, out_dir)
    if output_md_path is None:
        logging.error(f"DCC: failed {output_md_path} @convert_doc_to_md_by_llamaparse")
        return None, None 

    md_info_path = find_md_info_path(output_md_path)
    output_md_path, md_info = fix_ocr_content_by_gpt(md_info_path)
    if md_info is None:
        logging.error(f"DCC: failed {output_md_path} @fix_ocr_content_by_gpt")
        return None, None 

    output_md_path, md_info = fix_img_content_by_lvlm(md_info_path)
    if md_info is None:
        logging.error(f"DCC: failed {output_md_path} @fix_img_content_by_lvlm")
        return None, None 

    output_md_path, md_info = fix_markdown_headings(md_info_path)
    if md_info is None:
        logging.error(f"DCC: failed {output_md_path} @fix_markdown_headings")
        return None, None 

    output_md_path, md_info = fix_markdown_content_for_hiqa(md_info_path)
    if md_info is None:
        logging.error(f"DCC: failed {output_md_path} @fix_markdown_content_for_hiqa")
        return None, None 

    final_md_path = make_final_md(md_info_path, md_info)

    return final_md_path

if __name__ == "__main__":
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    doc_pathname = "datasrc/exam/raw_docs/Long Context LLMs Meet RAG_compressed.pdf"

    out_dir = f"_work/ctn2md_{random.randint(10,99)}"
    print(f"out_dir: {out_dir}")

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    dst_path = do_content2md_convert(doc_pathname, out_dir)
    print(dst_path)

    md_info_path = find_md_info_path(dst_path)
    print(md_info_path)
    md_info = load_md_info(md_info_path)
    rich.print(md_info)