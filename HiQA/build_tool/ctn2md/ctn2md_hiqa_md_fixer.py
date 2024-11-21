from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import re
#import random
#import json
#import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info


def fix_markdown_content_for_hiqa(md_info_path):
    out_dir = os.path.dirname(md_info_path)
    md_info = load_md_info(md_info_path)
    if md_info is None:
        return None, None 

    fname_output_s2_md = md_info.get("fname_output_s2_md", None)
    if fname_output_s2_md is None:
        return None, None 

    pname_s2 = os.path.join(out_dir, fname_output_s2_md)
    with open(pname_s2, "r", encoding="utf8") as f:
        md_text = f.read()
        rich.print(md_text)

    #md_text_new = filter_markdown_images(md_text, out_dir, md_info)
    md_text_new = md_text

    fname_s3_md_name = os.path.basename(fname_output_s2_md).replace("_s2.md", "_s3.md")
    fname_output_s3_md = os.path.join(out_dir, fname_s3_md_name)
    with open(fname_output_s3_md, "w+") as f:
        f.write(md_text_new)

    logging.info(f"fname_s3_md_name: {fname_s3_md_name}")
    if isinstance(md_info, dict):
        md_info["fname_output_s3_md"] = os.path.basename(fname_output_s3_md)
        save_md_info(out_dir, md_info)
    return fname_output_s2_md, md_info    


if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_exam0/info.json"
    md_info_path = "_work/ctn2md_chatgpt/info.json"
    md_info_path, md_info = fix_markdown_content_for_hiqa(md_info_path)
    print(md_info_path)
    rich.print(md_info)