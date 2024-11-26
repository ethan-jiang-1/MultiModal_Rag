from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import json
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src.ctn2md_llamaparse_md_generater import gen_md_llamaparse
from ctn2md.src.ctn2md_fix_heading_plc import fix_headings_plc_by_gpt
from ctn2md.src.ctn2md_fix_content_ocr import fix_content_ocr_by_gpt
from ctn2md.src.ctn2md_fix_img_reference import fix_img_reference_by_lvlm
from ctn2md.src.ctn2md_fix_section_hierarchy_numbers import fix_section_heirarchy_numbers
from ctn2md.src.ctn2md_fix_section_hierarchy_comments import fix_section_heirarchy_comments


# TODO: ethan_bm25 keywords for bm25 at doc level
def _make_final_md(md_info_path):
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


def _do_content2md_convert_core(ctn_pathname, out_dir=None, skip_gen=False, section_by_number=False):
    if out_dir is None:
        out_dir = MdInfo.get_suggested_out_dir(ctn_pathname)
    logging.warning(f"work out_dir: {out_dir}")
    os.makedirs(out_dir, exist_ok=True)

    if not skip_gen:
        md_info_path = gen_md_llamaparse(ctn_pathname, out_dir)
        if md_info_path is None:
            logging.error(f"DCC: failed {md_info_path} @convert_doc_to_md_by_llamaparse")
            return None, None 
    else:
        md_info = MdInfo(out_dir)
        md_info_path = md_info.get_md_info_path()
        pathname_s0_md = md_info.name_step_pathname(0)
        if (pathname_s0_md is None) or (not os.path.exists(pathname_s0_md)):
            raise ValueError(f"{pathname_s0_md} not exist, you have to generate it first")

    md_info_path = fix_content_ocr_by_gpt(md_info_path, src_step_num=0)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_content_ocr_by_gpt")
        return None, None 

    md_info_path = fix_headings_plc_by_gpt(md_info_path, src_step_num=1)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_headings_llamaparse")
        return None, None 

    md_info_path = fix_img_reference_by_lvlm(md_info_path, src_step_num=2)
    if md_info_path is None:
        logging.error(f"DCC: failed {md_info_path} @fix_img_reference_by_lvlm")
        return None, None 

    if section_by_number:
        md_info_path = fix_section_heirarchy_numbers(md_info_path, src_step_num=3)
        if md_info_path is None:
            logging.error(f"DCC: failed {md_info_path} @fix_section_heirarchy_numbers")
            return None, None 
    else:
        md_info_path = fix_section_heirarchy_comments(md_info_path, src_step_num=3)
        if md_info_path is None:
            logging.error(f"DCC: failed {md_info_path} @fix_section_heirarchy_comments")
            return None, None         

    final_md_path = _make_final_md(md_info_path)

    return final_md_path

def do_content2md_convert(ctn_pathname, out_dir=None, skip_gen=False, section_by_number=False):
    final_md_path = None
    try:
        final_md_path = _do_content2md_convert_core(ctn_pathname,
                                                    out_dir=out_dir,
                                                    skip_gen=skip_gen,
                                                    section_by_number=section_by_number)
    except Exception as ex:
        logging.exception(ex)
    return final_md_path

if __name__ == "__main__":
    setup_logger_handlers()
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）.pdf"
    #doc_pathname = "datasrc/test/raw_docs/高效沟通之黄金三角模型课程大纲.docx"

    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/Long-Context LLMs Meet RAG_compressed.pdf"
    doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/0530-大模型微调培训-VisualGLM.pdf"

    out_dir = None
    skip_gen = True 

    final_md_path = _do_content2md_convert_core(doc_pathname, out_dir=out_dir, skip_gen=skip_gen)
    print(final_md_path)

    md_info = MdInfo(final_md_path)
    rich.print(md_info)
    print(final_md_path)