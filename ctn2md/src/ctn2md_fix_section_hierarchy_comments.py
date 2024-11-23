from dotenv import load_dotenv
#import os
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

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo


def filter_headings_for_hierarchy_comments(md_text, md_info):
    """
    在 Markdown 文本的每个标题前插入基于层级的描述注释。

    :param md_text: 原始 Markdown 文本
    :return: 带描述注释的 Markdown 文本
    """
    lines = md_text.strip().split('\n')
    processed_lines = []
    hierarchy_stack = []  # 用于维护标题的层级
    doc_title = None  # 用于保存文档标题（第一个一级标题）

    for line in lines:
        # 检测是否是标题行
        if line.startswith("#"):
            level = line.count("#")  # 根据 # 的数量确定标题层级
            title = line[level:].strip()  # 提取标题内容

            # 如果是第一个一级标题，定义文档标题
            if level == 1 and not doc_title:
                doc_title = title
                hierarchy_stack = []  # 初始化层级堆栈
            else:
                # 调整堆栈以匹配当前标题的层级
                while len(hierarchy_stack) >= level:
                    hierarchy_stack.pop()
                hierarchy_stack.append(title)  # 添加当前标题到堆栈

            # 生成描述信息
            desc = f"<!-- [desc] {doc_title} __ {' __ '.join(hierarchy_stack)} [desc] -->"

            # 插入描述注释
            processed_lines.append("")
            processed_lines.append(desc)

        # 无论是否是标题行，都保留原始行
        processed_lines.append(line)

    # 将处理后的内容重新组合为 Markdown 文本
    return "\n".join(processed_lines)


def fix_section_heirarchy_comments(md_info_path, src_step_num=None, dst_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = filter_headings_for_hierarchy_comments(md_text, md_info)

    logging.warning(f"fix_section_heirarchy_comments: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new)
    
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_section_heirarchy_comments")
    md_info_path = md_info.save()
    return md_info_path    


if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 3
    dst_step_num = 41
    md_info_path = "_work/ctn2md_时代的人力资源管理进化(徐刚)/_info.json"

    md_info_path = fix_section_heirarchy_comments(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)