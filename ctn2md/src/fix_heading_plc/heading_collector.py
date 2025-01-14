"""
标题收集和预处理模块
负责标题的收集、规范化和初始处理
"""
from typing import Tuple
from dotenv import load_dotenv
load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo, MIFN
from ctn2md.md_info.md_process_plc import (
    inject_plc_comment_to_page,
    separate_heading_and_plc_comment,
    get_all_normalized_headings_with_plc_info,
    has_injected_plc_comment
)
import logging

def _normalize_markdown_heading_plc(md_text: str, md_info: MdInfo) -> str:
    """
    规整化 Markdown 的 heading 写法，确保所有 heading 的 # 与内容之间仅有一个空格。

    参数:
        md_text (str): 输入的 Markdown 字符串流。
        md_info (str): 输出文件的名称信息。

    返回:
        str: 规整化后的 Markdown 字符串。
    """
    normalized_lines, heading_n_plc_lines, first_line_no_heading = get_all_normalized_headings_with_plc_info(md_text)

    # 生成规整化的 Markdown 内容
    normalized_md = "\n".join(normalized_lines)

    heading_first_line, plc_comment_first_line = "", ""
    if first_line_no_heading is not None and len(first_line_no_heading) > 0:
        heading_first_line, plc_comment_first_line = separate_heading_and_plc_comment(first_line_no_heading)

    md_info[MIFN.FHL_ORG] = {
        "org_doc_title": md_info.get_doc_title(),
        "org_doc_type": md_info.get_ctn_type(),
        "org_first_line": (heading_first_line, plc_comment_first_line),
        "org_heading_lines": heading_n_plc_lines
    }
    md_info.save()
                
    return normalized_md

def _fix_markdown_with_no_heading(md_text: str, md_info: MdInfo) -> str:
    """
    为没有标题的 Markdown 文本添加标题。

    参数:
        md_text (str): Markdown 文本
        md_info (MdInfo): Markdown 文件信息对象

    返回:
        str: 添加标题后的 Markdown 文本
    """
    doc_title = md_info.get_doc_title()
    heading_line = "# " + doc_title + "\n\n"
    new_md_text = heading_line + md_text
    return inject_plc_comment_to_page(new_md_text, 1, 1, md_info)

def collect_fhl_info(md_info: MdInfo, md_full_text: str) -> Tuple[dict, str]:
    """
    收集和处理标题层级信息。

    参数:
        md_info (MdInfo): Markdown 文件信息对象
        md_full_text (str): 完整的 Markdown 文本

    返回:
        Tuple[dict, str]: (标题层级信息字典, 处理后的 Markdown 文本)
    """
    fname_org_doc = md_info.get("fname_org_doc", "unknown")
    logging.info(f"Collecting headings from {fname_org_doc}")
    
    md_full_text_new = _normalize_markdown_heading_plc(md_full_text, md_info)
    fhl_org = md_info[MIFN.FHL_ORG]

    org_heading_lines = fhl_org["org_heading_lines"]
    if (len(org_heading_lines)) == 0 or (not has_injected_plc_comment(md_full_text)):
        logging.warning(f"No headings or missing PLC comments in {fname_org_doc}, applying fixes")
        md_full_text_new = _fix_markdown_with_no_heading(md_full_text_new, md_info)
        md_full_text_new = _normalize_markdown_heading_plc(md_full_text_new, md_info)
        fhl_org = md_info[MIFN.FHL_ORG]

    return fhl_org, md_full_text_new
