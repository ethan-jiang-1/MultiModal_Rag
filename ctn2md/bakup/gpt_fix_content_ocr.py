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


class OFM:  # OCR Fix Mothod
    BY_SKIP = "ofm_skip"
    BY_CONTENT = "ofm_content"
    BY_PAGE = "ofm_page"
    BY_AUTO = "ofm_auto"

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.utils_llm.llm_fix_ocr_md import fix_ocr_self_correct_markdown
from ctn2md.src.md_info_base import MdInfo, MIFN

#TODO: ethan_ocr_in_gen_only: we should get rid of OCR in the flow -- push to when it generate the markdown, otherwise the logic is way to complicated to handle
def _fix_ocr_by_stiche_pages(md_text, md_info):
    fnames_pages = md_info.get_fnames_pages()
    if not fnames_pages:
        raise ValueError("fnames_pages is empty")
    
    md_text_fixed = ""
    out_dir = md_info.get_out_dir()
    question_num = 8000
    total_pages = len(fnames_pages)
    model = "gpt-4o"  # has to be gpt-4o
    if total_pages >= 5:
        model = "gpt-4o-mini"
        logging.warning(f"_fix_ocr_by_stiche_pages: total_pages: {total_pages}, it may take a while....")
    else:
        logging.info(f"_fix_ocr_by_stiche_pages: total_pages: {total_pages}")
    for ndx, fname_page in enumerate(fnames_pages):
        pathname = os.path.join(out_dir, fname_page)
        with open(pathname, 'r', encoding='utf8') as f:
            md_page = f.read()
        ctn_type = md_info.get_ctn_type()

        logging.info(f"_fix_ocr_by_stiche_pages: current_page: {ndx+1} / total_pages: {total_pages}...")
        md_page_fixed = fix_ocr_self_correct_markdown(md_page, ctn_type, model=model, question_num=question_num) 
        md_text_fixed += md_page_fixed + "\n"
        question_num += 1

    return md_text_fixed      

def _fix_ocr_by_proc_whole(md_text, md_info):
    ctn_type = md_info.get_ctn_type()
    md_text_fixed = fix_ocr_self_correct_markdown(md_text, ctn_type)  
    return md_text_fixed

def _find_ofm_and_reason(md_text, md_info):
    ofm = md_info.get_md_control("mctl_ofm", None)
    ofm_reason = ""
    if ofm is None or ofm == OFM.BY_AUTO:
        ofm = md_info.get_md_params("mp_ofm", OFM.BY_SKIP)
        ofm_reason = md_info.get_md_params("mp_ofm_reason", "skip ?unknown")
    else:
        ofm_reason = "mctl_control"
    return ofm, ofm_reason

def fix_content_ocr_by_gpt(md_info_path, src_step_num=None, dst_step_num=None, ofm=None):
    logging.info(f"##MDFLOW##: fix_content_ocr_by_gpt started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    ofm, ofm_reason = _find_ofm_and_reason(md_text, md_info)
    ofm_info = {"ofm": ofm,
                "ofm_reason": ofm_reason}
    md_info[MIFN.OFM_INFO] = ofm_info
    logging.info(f"OFM: ofm:{ofm} ofm_reason: {ofm_reason}")
    if ofm == OFM.BY_CONTENT:
        md_text_fixed = _fix_ocr_by_proc_whole(md_text, md_info)
    elif ofm == OFM.BY_PAGE:
        md_text_fixed = _fix_ocr_by_stiche_pages(md_text, md_info)
    elif ofm == OFM.BY_SKIP:
        md_text_fixed = md_text
    else:
        raise ValueError(f"unknown ofm: {ofm}")

    logging.warning(f"fix_content_ocr_by_gpt: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_fixed)
    
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_content_ocr_by_gpt", extra=f"{ofm}:{ofm_reason}")
    md_info_path = md_info.save()
    logging.info(f"##MDFLOW##: fix_content_ocr_by_gpt ended:  ofm:{ofm} ofm_reason: {ofm_reason}")
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    ofm = None
    src_step_num = 0
    #md_info_path = "_work/ctn2md_exam5/info.json"

    #ofm = OFM.BY_PAGE
    #md_info_path = "_work/ctn2md_stream1/info.json"

    #md_info_path = "_work/ctn2md_时代的人力资源管理进化(徐刚)/_info.json"
    #md_info_path = "_work/ctn2md_座椅STO间隙 P1/_info.json"
    #md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"

    dst_step_num = 11
    md_info_path = "_work/ctn2md_-波士顿咨询：银行业生成式AI应用报告（2023）/_info.json"

    md_info_path = fix_content_ocr_by_gpt(md_info_path, ofm=ofm, src_step_num=src_step_num, dst_step_num=dst_step_num)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)
