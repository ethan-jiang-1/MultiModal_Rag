from dotenv import load_dotenv
#import os
import sys
#import logging
import rich
import re
#import random
#import json
#import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import MdInfo
from HiQA.build_tool.utils_bt.llm_fix_heading_lvl import fix_heading_lvl_markdown

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
                # 统计当前标题的内容字符数
                content_text = ''.join(current_content).replace(' ', '').replace('\n', '')
                heading_content_counts[current_heading] = len(content_text)
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

def fix_headings_llamaparse(md_info_path, src_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = filter_markdown_heading_llamapase(md_text, md_info)
    count_markdown_heading_content(md_text_new, md_info)

    fhl = md_info["fhl"]
    fhl_map = fix_heading_lvl_markdown(fhl)
    rich.print(fhl_map)

    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new)
    
    md_info.add_step_into_md_info_streams(pathname_dst_step_md, actor="fix_headings_llamaparse")
    md_info_path = md_info.save()
    return md_info_path 

if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_stream0/info.json"
    md_info_path = "_work/ctn2md_s3_0/info.json"
    md_info_path = fix_headings_llamaparse(md_info_path, src_step_num=0)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)