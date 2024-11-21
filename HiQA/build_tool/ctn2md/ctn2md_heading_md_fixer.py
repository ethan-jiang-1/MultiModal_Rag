from dotenv import load_dotenv
import os
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

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info

def filter_markdown_heading(md_text, out_dir, md_info):
    """
    规整化 Markdown 的 heading 写法，确保所有 heading 的 # 与内容之间仅有一个空格。

    参数:
        md_text (str): 输入的 Markdown 字符串流。
        out_dir (str): 输出的目录路径。
        md_info (str): 输出文件的名称信息。

    返回:
        str: 规整化后的 Markdown 字符串。
    """
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

def fix_markdown_headings(md_info_path):
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

    md_text_new = filter_markdown_heading(md_text, out_dir, md_info)

    fname_s3_md_name = os.path.basename(fname_output_s2_md).replace("_s2.md", "_s3.md")
    fname_output_s3_md = os.path.join(out_dir, fname_s3_md_name)
    with open(fname_output_s3_md, "w+") as f:
        f.write(md_text_new)

    logging.info(f"fname_s3_md_name: {fname_s3_md_name}")
    if isinstance(md_info, dict):
        md_info["fname_output_s3_md"] = os.path.basename(fname_output_s3_md)
        save_md_info(out_dir, md_info)
    return fname_output_s3_md, md_info    


if __name__ == "__main__":
    setup_logger_handlers()

    #md_info_path = "_work/ctn2md_exam0/info.json"
    #md_info_path = "_work/ctn2md_chatgpt/info.json"
    md_info_path = "_work/ctn2md_backpanel/info.json"
    output_md_path, md_info = fix_markdown_headings(md_info_path)
    print(output_md_path)
    rich.print(md_info)