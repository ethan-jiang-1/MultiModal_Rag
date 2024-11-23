from dotenv import load_dotenv
#import os
import sys
import logging
import rich
import re
#import random
#import json
#import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils_llm.llm_fix_heading_lvl import fix_heading_lvl_markdown
from ctn2md.utils.util_markdown import extract_pure_text_from_markdown

def filter_markdown_heading_llamapase(md_text, md_info):
    """
    规整化 Markdown 的 heading 写法，确保所有 heading 的 # 与内容之间仅有一个空格。

    参数:
        md_text (str): 输入的 Markdown 字符串流。
        md_info (str): 输出文件的名称信息。

    返回:
        str: 规整化后的 Markdown 字符串。
    """

    #out_dir = md_info.get_out_dir()
    # 定义正则匹配 Markdown Heading 的模式
    heading_pattern = r"^(#{1,6})(\s*)(.+)$"
    
    heading_lines = []
    # 规整化处理 Markdown 文本
    normalized_lines = []
    org_lines = md_text.splitlines()
    for line in org_lines:
        match = re.match(heading_pattern, line)
        if match:
            # 提取 # 符号 和 heading 的内容
            hashes = match.group(1)
            content = match.group(3).strip()  # 去掉多余的空格
            normalized_line = f"{hashes} {content}"
            normalized_lines.append(normalized_line)
            heading_lines.append(normalized_line)
        else:
            normalized_lines.append(line)

    # 生成规整化的 Markdown 内容
    normalized_md = "\n".join(normalized_lines)

    md_info["fhl"] = {"org_doc_title": md_info.get_doc_title(),
                      "org_doc_type": md_info.get_ctn_type(),
                      "org_first_line": org_lines[0],
                      "org_heading_lines": heading_lines}
    md_info.save()
                
    return normalized_md

def count_markdown_heading_content(md_text, md_info):
    """
    统计 Markdown 文本中每个 heading (以 # 开头) 的内容字符数（去除空白）。

    :param md_text: Markdown 文本内容
    :param md_info: 文档信息（文件名等）
    :return: 一个字典，key 为标题内容，value 为标题后内容的字符数
    """
    # 定义正则匹配 Markdown Heading 的模式
    heading_pattern = r"^(#{1,6})\s*(.+)$"

    # 分割 Markdown 文本的行
    lines = md_text.splitlines()
    
    # 用于存储每个标题的内容字符数
    heading_content_counts = {}

    current_heading = None
    current_content = []

    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            # 如果匹配到新的 heading
            if current_heading is not None:
                # 统计当前标题的内容字符数 (为刚才过去的heading)
                pure_content_text = extract_pure_text_from_markdown(''.join(current_content))
                heading_content_counts[current_heading] = len(pure_content_text)
            # 更新当前标题
            current_heading = match.group(0).strip()
            current_content = []
        else:
            # 非标题行，加入当前标题的内容
            current_content.append(line.strip())

    # 处理最后一个标题的内容
    if current_heading is not None:
        content_text = ''.join(current_content).replace(' ', '').replace('\n', '')
        heading_content_counts[current_heading] = len(content_text)
    fhl = md_info.get("fhl")
    if fhl is not None:
        org_heading_lines = fhl.get("org_heading_lines")
        for ndx, heading_line in enumerate(org_heading_lines):
            cnt = heading_content_counts.get(heading_line, 0)
            org_heading_lines[ndx] = (heading_line, cnt)
        md_info.save()
    return heading_content_counts

def update_markdown_heading_content(md_text, md_info, fhl_map):
    """
    替换 Markdown 文本中的标题内容，根据 fhl_map 提供的替换规则。

    :param md_text: Markdown 文本
    :param md_info: Markdown 文件的基本信息
    :param fhl_map: 包含映射规则的 JSON 字典
    :return: 替换后的 Markdown 文本 new_md_text 和未处理的 fhl_map 副本
    """
    import copy

    # 创建 fhl_map 的副本以进行替换操作
    fhl_map_copy = copy.deepcopy(fhl_map)

    # 提取映射规则
    first_line_map = fhl_map_copy.get("first_line_map", {})
    heading_lines_map = fhl_map_copy.get("heading_lines_map", [])

    # 初始化结果 Markdown 文本
    lines = md_text.splitlines()
    new_lines = []

    # 标记哪些 heading_lines_map 的项已被处理
    used_indices = set()

    # 处理第一行
    if lines:
        first_line = lines[0].strip()
        if first_line_map and "mapped_line" in first_line_map:
            if first_line.startswith("#"):
                for i, item in enumerate(heading_lines_map):
                    if i in used_indices:
                        continue
                    if item["original_line"] == first_line:
                        new_lines.append(item["mapped_line"])
                        used_indices.add(i)
                        break
                else:
                    new_lines.append(first_line_map["mapped_line"])
            else:
                new_lines.append(first_line_map["mapped_line"])
        else:
            new_lines.append(first_line)

    # 逐行处理剩余内容
    for line in lines[1:]:
        stripped_line = line.strip()
        replaced = False

        for i, item in enumerate(heading_lines_map):
            if i in used_indices:
                continue
            if item["original_line"] == stripped_line:
                new_lines.append(item["mapped_line"])
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


def fix_headings_llamaparse(md_info_path, src_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = filter_markdown_heading_llamapase(md_text, md_info)
    count_markdown_heading_content(md_text_new, md_info)

    fhl_org = md_info["fhl"]
    #rich.print(fhl)
    fhl_map = fix_heading_lvl_markdown(fhl_org)
    #rich.print(fhl_map)
    rich.print(fhl_map)
    rich.print({"org_heading_lines": fhl_map["org_heading_lines"],
                "new_heading_lines": fhl_map["new_heading_lines"]})

    md_text_new1, unprocessed_heading_lines_map = update_markdown_heading_content(md_text_new, md_info, fhl_map)
    rich.print(unprocessed_heading_lines_map)

    logging.warning(f"fix_headings_llamaparse: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new1)
    
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_headings_llamaparse")
    md_info_path = md_info.save()
    return md_info_path 

if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_work/ctn2md_时代的人力资源管理进化(徐刚)"
    src_step_num = 1

    md_info_path = fix_headings_llamaparse(md_info_path, src_step_num=src_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)