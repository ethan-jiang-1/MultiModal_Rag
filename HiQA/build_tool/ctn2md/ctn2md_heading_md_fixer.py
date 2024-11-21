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

def filter_markdown_heading(md_text, md_info):
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
    
    # 规整化处理 Markdown 文本
    normalized_lines = []
    for line in md_text.splitlines():
        match = re.match(heading_pattern, line)
        if match:
            # 提取 # 符号 和 heading 的内容
            hashes = match.group(1)
            content = match.group(3).strip()  # 去掉多余的空格
            normalized_line = f"{hashes} {content}"
            normalized_lines.append(normalized_line)
        else:
            normalized_lines.append(line)

    # 生成规整化的 Markdown 内容
    normalized_md = "\n".join(normalized_lines)
    return normalized_md

def fix_markdown_headings(md_info_path, src_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = filter_markdown_heading(md_text, md_info)

    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new)
    
    md_info.add_step_into_md_info_streams(pathname_dst_step_md, actor="fix_markdown_headings")
    md_info_path = md_info.save()
    return md_info_path 

if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_work/ctn2md_stream1/info.json"
    md_info_path = fix_markdown_headings(md_info_path, src_step_num=2)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)