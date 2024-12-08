from dotenv import load_dotenv
#import os
import sys
import logging
import rich
#import re
#import random
#import json
#import json_repair
import copy

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.utils_llm.llm_fix_heading_lvl_gpt import fix_heading_lvl_markdown_by_gpt
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.src.md_process_plc import inject_plc_comment_to_page, separate_heading_and_plc_comment, get_all_normalized_headings_with_plc_info

def _filter_markdown_heading_plc(md_text, md_info):
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

    md_info[MIFN.FHL_ORG] = {"org_doc_title": md_info.get_doc_title(),
                             "org_doc_type": md_info.get_ctn_type(),
                             "org_first_line": (heading_first_line, plc_comment_first_line),
                             "org_heading_lines": heading_n_plc_lines}
    md_info.save()
                
    return normalized_md

def _fix_markdown_with_no_heading(md_text, md_info):
    doc_title = md_info.get_doc_title()
    heading_line = "# " + doc_title + "\n\n"
    new_md_text = heading_line + md_text
    return inject_plc_comment_to_page(new_md_text, 1, 1, md_info)


def _update_markdown_heading_content(md_text, md_info, fhl_map):
    """
    替换 Markdown 文本中的标题内容，根据 fhl_map 提供的替换规则。

    :param md_text: Markdown 文本
    :param md_info: Markdown 文件的基本信息
    :param fhl_map: 包含映射规则的 JSON 字典
    :return: 替换后的 Markdown 文本 new_md_text 和未处理的 fhl_map 副本
    """

    # 创建 fhl_map 的副本以进行替换操作
    fhl_map_copy = copy.deepcopy(fhl_map)

    # 提取映射规则
    heading_lines_map = fhl_map_copy.get("optimized_heading_lines_map", [])
    if len(heading_lines_map) == 0:
        raise ValueError("UMHC: heading_lines_map == [] ?!")

    # 初始化结果 Markdown 文本
    lines = md_text.splitlines()
    new_lines = []

    # 标记哪些 heading_lines_map 的项已被处理
    used_indices = set()

    for line in lines:
        stripped_line = line.strip()
        replaced = False

        if stripped_line.startswith("#"):
            for i, item in enumerate(heading_lines_map):
                if i in used_indices:
                    continue
                if stripped_line.startswith(item["original_line"]):
                    new_line = item["mapped_line"]
                    if new_line is None:
                        new_line = ""
                    new_lines.append(new_line)
                    used_indices.add(i)
                    replaced = True
                    break

        if not replaced:
            new_lines.append(line)

    # 检查未处理的 heading_lines_map 项
    unprocessed_heading_lines_map = [
        item for i, item in enumerate(heading_lines_map) if i not in used_indices
    ]
    fhl_map_copy["unprocessed_heading_lines_map"] = unprocessed_heading_lines_map

    # 生成新的 Markdown 文本
    new_md_text = "\n".join(new_lines)

    return new_md_text, unprocessed_heading_lines_map


def fix_headings_plc_by_llm(md_info_path, src_step_num=None, dst_step_num=None):
    logging.info(f"##MDFLOW##: fix_headings_plc_by_llm started src_step_num:{src_step_num} dst_step_num:{dst_step_num}...")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = _filter_markdown_heading_plc(md_text, md_info)

    fhl_org = md_info[MIFN.FHL_ORG]
    org_heading_lines = fhl_org["org_heading_lines"]
    if len(org_heading_lines) == 0:
        md_text_new = _fix_markdown_with_no_heading(md_text_new, md_info)
        md_text_new = _filter_markdown_heading_plc(md_text_new, md_info)
        fhl_org = md_info[MIFN.FHL_ORG]
    
    mctrl_fix_heading_model = md_info.get_md_control("mctrl_fix_heading_model", "gpt")
    if mctrl_fix_heading_model == "gpt":
        model = "gpt-4o" # so far, only gpt-4o can handle this well,  gpt-4o-mini does not.
        fhl_map = fix_heading_lvl_markdown_by_gpt(fhl_org, ctn_type=md_info.get_ctn_type(), model=model)
    else:
        raise ValueError(f"not implemented yet for using {mctrl_fix_heading_model} in fix_headings_plc_by_llm")

    #rich.print(fhl_map)
    rich.print(fhl_map)
    optimized_heading_lines_map = fhl_map["optimized_heading_lines_map"]
    o2n_map = {"org_heading_lines": [item["original_line"] for item in optimized_heading_lines_map],
               "new_heading_lines": [item["mapped_line"] for item in optimized_heading_lines_map]}
    rich.print(o2n_map)

    # TODO: ethan_finial_md we need fix the page_md as well, as the final full md are come from indivdual page_md
    # do we really need make dependence on page_md? better get rid of such dependence
    md_text_new1, unprocessed_heading_lines_map = _update_markdown_heading_content(md_text_new, md_info, fhl_map)
    rich.print(unprocessed_heading_lines_map)

    logging.warning(f"fix_headings_plc_by_llm: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new1)
    
    md_info[MIFN.FHL_MAP_O2N] = o2n_map
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_headings_plc_by_llm")
    md_info_path = md_info.save()
    logging.info(f"##MDFLOW##: fix_headings_plc_by_llm ended: model: {model}")
    return md_info_path 

if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 0
    dst_step_num = 11
    md_info_path = "_output/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    #md_info_path = "_output/ctn2md_座椅STO间隙 P1/_info.json"

    md_info_path = fix_headings_plc_by_llm(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)