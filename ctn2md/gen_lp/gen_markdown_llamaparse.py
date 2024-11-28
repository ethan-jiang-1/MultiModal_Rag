from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lp.lp_revisit_result import post_scan_llamaparse_result
from ctn2md.gen_lp.lp_gen_normal_pages import gen_normal_pages
from ctn2md.gen_lp.lp_gen_premium_pages import gen_preminum_pages
   
def _save_final_md_from_pages(md_info):
    out_dir = md_info.get_out_dir()
    fnames_pages = md_info[MIFN.FNAMES_PAGES]
    pathname_step0 = md_info.name_step_pathname(0)

    full_md_text = ""
    for fname_page in fnames_pages:
        pname_page = os.path.join(out_dir, fname_page)
        with open(pname_page, "r") as f:
            md_text = f.read()
        if len(full_md_text) != 0:
            full_md_text += "\n"
        full_md_text += md_text

    with open(pathname_step0, "w+") as f: 
        f.write(full_md_text)
    return pathname_step0

def generate_markdown_llamaparse(md_info):
    out_dir = md_info.get_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    json_result = gen_normal_pages(md_info)

    target_pages = md_info.get_md_control("mctl_lp_premium_pages", None)
    if (target_pages is not None) and (len(target_pages) != 0):
        gen_preminum_pages(md_info)

    pathname_step0 = _save_final_md_from_pages(md_info)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor="gen_md_llamaparse")
    md_info.save()

    post_scan_llamaparse_result(md_info, json_result=json_result)

    doc_pathname = md_info.get_doc_pathname()
    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()
    
    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"

    md_info = MdInfo(md_info_path)

    ret = generate_markdown_llamaparse(md_info)
    rich.print(ret)