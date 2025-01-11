"""
标题层级处理模块
负责处理标题层级注入的核心逻辑
"""

from dotenv import load_dotenv

load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.utils.util_markdown import remove_comment
from ctn2md.src.inject_section_hierarchy.heading_stack import HeadingStack

def process_markdown_hierarchy(md_text:str, md_info: MdInfo) -> str:
    """
    在 Markdown 文本的每个标题前插入基于层级的描述注释，
    同时生成标题的章节编号，确保一级标题独立编号，子章节正确继承父级编号。
    支持容错处理输入的标题层级跳跃或逆序。

    :param md_text: 原始 Markdown 文本
    :param md_info: Markdown 信息对象
    :return: 处理后的 Markdown 文本
    """
    lines = md_text.strip().split('\n')
    processed_lines = []
    stack = HeadingStack()  # 使用堆栈对象
    md_info[MIFN.MD_SECTIONS] = []  # 初始化列表

    for line in lines:
        # 移除 <!-- ... --> 注释
        line = remove_comment(line)

        # 检测是否是标题行
        if line.startswith("#"):
            level = line.count("#")  # 根据 # 的数量确定标题层级
            title = line[level:].strip()  # 提取标题内容

            # 一级标题：重置堆栈
            if level == 1:
                chapter_number = stack.push_level(level, title)  # 使用 push_level 更新堆栈
                ordered_name = f"{chapter_number}) {title}"
                hierarchy_desc = stack.get_hierarchy_desc()

                # 记录到 md_info
                md_info[MIFN.MD_SECTIONS].append({
                    "hierarchy_desc": hierarchy_desc,
                    "ordered_name": ordered_name
                })
            else:
                # 调整堆栈深度并添加标题
                chapter_number = stack.push_level(level, title)
                ordered_name = f"{chapter_number}) {title}"
                hierarchy_desc = stack.get_hierarchy_desc()

                # 记录到 md_info
                md_info[MIFN.MD_SECTIONS].append({
                    "hierarchy_desc": hierarchy_desc,
                    "ordered_name": ordered_name
                })

            # 生成描述注释
            desc = f"<!-- [ordered_name] {ordered_name} [ordered_name] [desc] {hierarchy_desc} [desc] -->"
            processed_lines.append("")
            processed_lines.append(desc)

        # 无论是否是标题行，都保留原始行
        processed_lines.append(line)

    # 返回处理后的 Markdown 文本
    return "\n".join(processed_lines) 