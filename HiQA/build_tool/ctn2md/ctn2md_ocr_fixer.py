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
from HiQA.build_tool.util_md.llm_fix_ocr_md import fix_ocr_self_correct_markdown
from HiQA.build_tool.ctn2md.ctn2md_base import save_md_info, load_md_info
from HiQA.build_tool.ctn2md.ctn2md_llamaparse_scan_info import should_llm_ocr_fix


def fix_ocr_content_by_gpt(md_info_path):
    out_dir = os.path.dirname(md_info_path)
    md_info = load_md_info(md_info_path)
    if md_info is None:
        return None, None 

    fname_output_s0_md = md_info.get("fname_output_s0_md", None)
    if fname_output_s0_md is None:
        return None, None 

    pname_s0 = os.path.join(out_dir, fname_output_s0_md)
    with open(pname_s0, "r", encoding="utf8") as f:
        md_text = f.read()

    fname_s1_md_name = os.path.basename(fname_output_s0_md).replace("_s0.md", "_s1.md")
    fname_output_s1_md = os.path.join(out_dir, fname_s1_md_name)

    if should_llm_ocr_fix(md_info):
        md_text_fixed = fix_ocr_self_correct_markdown(md_text)
    else:
        logging.warning("skip llm ocr fix as it is well structured md")
        md_text_fixed = md_text

    with open(fname_output_s1_md, "w+") as f:
        f.write(md_text_fixed)

    logging.info(f"fname_output_s1_md: {fname_output_s1_md}")
    md_info["fname_output_s1_md"] = os.path.basename(fname_s1_md_name)
    md_info_path = save_md_info(out_dir, md_info)
    return md_info_path, md_info

if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_work/ctn2md_exam5/info.json"
    md_info_path, md_info = fix_ocr_content_by_gpt(md_info_path)
    print(md_info_path)
    rich.print(md_info)
