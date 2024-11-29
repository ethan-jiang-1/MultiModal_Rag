from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.utils_llm.llm_summarize_content import summarize_doc_keywords
from ctn2md.utils.util_markdown import remove_comment
from ctn2md.src.md_info_base import MdInfo, MIFN

def summarize_content_by_gpt(md_info_path, src_step_num=None, dst_step_num=None):
    logging.info(f"##MDFLOW##: summarize_content_by_gpt started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, _ = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None:
        raise ValueError(f"no {pathname_src_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        full_content = f.read()
    full_content = remove_comment(full_content)

    doc_title = md_info.get_doc_title()

    resp = summarize_doc_keywords(doc_title, full_content)
    rich.print(resp)

    pathname_final_md_fname = md_info.name_step_pathname(-1)
    pathname_final_json_fname = pathname_final_md_fname.replace(".md", ".sum.json")
    json_str = json.dumps(resp, ensure_ascii=False, indent=4)
    with open(pathname_final_json_fname, 'w+', encoding='utf8') as f:
        f.write(json_str)

    md_info[MIFN.FNAME_FINAL_SUM] = os.path.basename(pathname_final_json_fname)
    md_info_path = md_info.save()
    logging.info(f"##MDFLOW##: summarize_content_by_gpt ended.")
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 4

    #md_info_path = "_work/ctn2md_前后排座椅间距定义 P1/_info.json"
    md_info_path = "_work/ctn2md_高效沟通之黄金三角模型课程大纲/_info.json"

    md_info_path = summarize_content_by_gpt(md_info_path, src_step_num=src_step_num)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)
