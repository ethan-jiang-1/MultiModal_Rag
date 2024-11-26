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
from ctn2md.utils.util_markdown import remove_comment

HIQA_MD_STYLE = """
##1. 要求格式为,PDF文本中的每一章节都作为markdown中的一个一级标题(只用一个 # 号)章节,
     无论章节还是子章节的标题,都要用markdown的一级标题表示,我们将用章节的编号来标记章节的级别。
     该章节的内容从这一章节的标题的后一行开始写。

##2. 关于章节和编号,对于PDF中的一切章节,子章节,都要在markdown中对应一个一级标题章节(一个# 章节）并且用章节的编号来表示级别,
     而非多个#,章节编号均为"x.x.x. XXXX"的格式

##3. 章节编号请使用阿拉伯数字,请使用小数点'.'作为编号间隔符,请严格遵循上下文的编号,如上一段为 '# 3. '时,其子章节为 '# 3.2. '

"""

def _filter_headings_for_heirarchy_numbers(md_text, md_info):
    """
    规整化 Markdown 的标题写法，为所有标题编号，并移除行中的 <!--... --> 注释。

    参数:
        md_text (str): 输入的 Markdown 字符串流。
        md_info (str): 输出文件的名称信息。

    返回:
        str: 规整化后的 Markdown 字符串。
    """
    # 定义正则匹配 Markdown Heading 的模式
    heading_pattern = r"^(#{1,6})\s*(.+)$"

    # 初始化堆栈和编号
    stack = []
    result_lines = []

    for line in md_text.splitlines():
        # 先移除行中的 <!-- ... --> 注释
        line = remove_comment(line)

        # 匹配标题行
        match = re.match(heading_pattern, line)
        if match:
            hashes = match.group(1)  # 标题等级 (e.g., #, ##, ###)
            title = match.group(2).strip()  # 标题内容
            level = len(hashes)  # 标题等级数 (1 = 一级标题, 2 = 二级标题, 等等)

            # 更新堆栈编号
            while len(stack) > level:  # 弹出多余的层级
                stack.pop()
            if len(stack) < level:
                stack.append(1)  # 新层级从1开始
            else:
                stack[-1] += 1  # 当前层级编号加1

            # 重置下级的编号
            for _ in range(len(stack), level):
                stack.append(1)

            # 生成编号
            numbering = ".".join(map(str, stack)) + "."  # e.g., "1.1.1."
            normalized_line = f"# {numbering} {title}"
            result_lines.append(normalized_line)
        else:
            # 非标题行原样保留
            result_lines.append(line)

    # 生成规整化后的 Markdown 内容
    normalized_md = "\n".join(result_lines)
    return normalized_md


def fix_section_heirarchy_numbers(md_info_path, src_step_num=None, dst_step_num=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_new = _filter_headings_for_heirarchy_numbers(md_text, md_info)

    logging.warning(f"fix_section_heirarchy_numbers: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_new)
    
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_section_heirarchy_numbers")
    md_info_path = md_info.save()
    return md_info_path    


if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 3
    dst_step_num = 40
    md_info_path = "_work/ctn2md_时代的人力资源管理进化(徐刚)/_info.json"

    md_info_path = fix_section_heirarchy_numbers(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)