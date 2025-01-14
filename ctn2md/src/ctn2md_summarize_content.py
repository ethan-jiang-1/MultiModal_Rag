from dotenv import load_dotenv
import os
import logging
import rich
import json

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MdInfo, MIFN
from ctn2md.src.summarize_content.make_doc_keywords import make_doc_keywords
from ctn2md.utils.util_markdown import remove_comment, read_markdown_file


def summarize_content_by_llm(md_info_path:str, src_step_num:int = None, dst_step_num:int = None) -> str:
    logging.info(f"##MDFLOW##: summarize_content_by_llm started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, _ = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None:
        raise ValueError(f"no {pathname_src_step_md}")

    full_content = read_markdown_file(pathname_src_step_md)
    full_content = remove_comment(full_content)

    doc_title = md_info.get_doc_title()

    doc_keywords = make_doc_keywords(md_info, doc_title, full_content)

    pathname_final_md_fname = md_info.name_step_pathname(-1)
    pathname_final_json_fname = pathname_final_md_fname.replace(".md", ".sum.json")
    # Convert Pydantic model to dict before JSON serialization
    resp_dict = doc_keywords.model_dump()
    json_str = json.dumps(resp_dict, ensure_ascii=False, indent=4)
    with open(pathname_final_json_fname, 'w+', encoding='utf8') as f:
        f.write(json_str)

    md_info[MIFN.FNAME_FINAL_SUM] = os.path.basename(pathname_final_json_fname)
    md_info_path = md_info.save()
    logging.info(f"##MDFLOW##: summarize_content_by_llm ended.")
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 2

    #md_info_path = "_output/ctn2md_前后排座椅间距定义 P1/_info.json"
    #md_info_path = "_output/ctn2md_高效沟通之黄金三角模型课程大纲/_info.json"
    #md_info_path = "_output/ctn2md_attention_is_all_you_need/_info.json"
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"

    md_info_path = summarize_content_by_llm(md_info_path, src_step_num=src_step_num)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)
