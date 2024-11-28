from dotenv import load_dotenv
#import os
import sys
#import logging
#import rich
#import random
import re

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

"""
    注释中参数解释 <!-- PLC: ... -->:
    1. Page:X/Y
        - X: 当前页码，从 1 开始计数。
        - Y: 文档总页数，由 total_pages 指定。
    2. Line:X/Y
        - X: 标题行在整个文档中的实际行号，从 1 开始计数。
        - Y: 文档的总行数。
    3. Chars:X/Y
        - X: 当前标题以下、下一个标题以上的字符数。
        - Y: 当前页面的总字符数，包含所有非图片内容。
"""
PLC_COMMENT = """<!-- PLC: Page:{current_page}/{total_pages}, Line:{line_number}/{total_lines}, Chars:{content_char_count}/{total_char_count} -->"""


def remove_plc_comment(line):
    """
    移除行中的 <!-- PLC: ... --> 注释。
    """
    return re.sub(r'<!-- PLC: .*? -->', '', line).strip()

def extract_plc_str_comment(line):
    """
    提取 Markdown 行中 <!-- PLC: XXX --> 的字符串内容。

    参数:
        line (str): Markdown 文本行。

    返回:
        str or None: 提取的字符串内容 (XXX)，如果没有 PLC 注释，返回 None。
    """
    match = re.search(r'<!-- PLC: (.*?) -->', line)
    if match:
        return match.group(1).strip()
    return None

def separate_heading_and_plc_comment(line):
    """
    分解 Markdown 标题行，提取前半部分的标题和后续的 PLC 注释。

    参数:
        line (str): Markdown 标题行，可能包含 <!-- PLC: ... --> 注释。

    返回:
        tuple: 包含两个元素的元组：
            - heading (str): 标题部分。
            - plc_comment (str or None): 提取的 PLC 注释内容（不包含 <!-- -->）。
                                        如果没有 PLC 注释，则为 None。
    """
    # 使用正则分解标题部分和 PLC 注释
    match = re.match(r'^(.*?)(<!-- PLC: (.*?) -->)?$', line.strip())
    if match:
        heading = match.group(1).strip()  # 提取标题部分
        plc_comment = match.group(3).strip() if match.group(3) else None  # 提取 PLC 注释内容
        return heading, plc_comment
    return line, ""  # 如果不匹配，返回原始行和 None

def extract_plc_comment(line):
    """
    提取 Markdown 行中 <!-- PLC: ... --> 的结构化内容。

    参数:
        line (str): Markdown 文本行。

    返回:
        dict or None: 提取的内容，返回字典包含 `Page`、`Line` 和 `Chars` 信息。
                      如果行中没有 PLC 注释，返回 None。
    """
    match = re.search(r'<!-- PLC: Page:(\d+)/(\d+), Line:(\d+)/(\d+), Chars:(\d+)/(\d+) -->', line)
    if match:
        return {
            "Page": {"current": int(match.group(1)), "total": int(match.group(2))},
            "Line": {"current": int(match.group(3)), "total": int(match.group(4))},
            "Chars": {"current": int(match.group(5)), "total": int(match.group(6))}
        }
    return ""


def inject_plc_comment_to_page(md_page, page_number, total_pages, md_info):
    """
    注入统计信息到 Markdown 文档标题行。
    :param md_page: str, 当前页面的 Markdown 内容
    :param page_ndx: int, 当前页码（从 0 开始计数）
    :param total_pages: int, 文档总页数
    :param md_info: dict, 包含整个文档的信息（例如标题等，暂未使用）
    :return: str, 注入统计信息后的 Markdown 文档内容
    """
    def count_chars(text):
        """
        统计文本中的字符数，忽略 Markdown 特殊符号和图片引用。
        """
        # 移除 Markdown 特殊符号和图片引用
        text = re.sub(r'[>#*_\-`~\[\]]', '', text)  # 去掉 Markdown 符号
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # 去掉图片引用
        text = re.sub(r'\s+', '', text)             # 去掉空白符
        return len(text)

    # 分割 Markdown 文档为行，并确定总行数
    lines = md_page.split('\n')
    total_lines = len(lines)

    # 使用正则提取标题和其内容范围
    sections = []
    current_section = {"title": None, "lines": []}

    for line in lines:
        if re.match(r'^#+\s', line):  # 如果是标题行
            # 如果当前有积累的标题范围，保存
            if current_section["title"]:
                sections.append(current_section)
            # 开始一个新的标题范围
            current_section = {"title": line, "lines": []}
        else:
            # 非标题行，归属于当前标题范围
            current_section["lines"].append(line)

    # 最后一个标题范围
    if current_section["title"]:
        sections.append(current_section)

    # 计算总字符数
    total_char_count = sum(
        count_chars(line) for line in lines
    )

    # 结果行列表
    result_lines = []
    for section in sections:
        title = section["title"]
        content_lines = section["lines"]
        content_char_count = sum(count_chars(line) for line in content_lines)

        # 注释信息
        line_number = lines.index(title) + 1
        injected_title = f"{title} "
        injected_title += PLC_COMMENT.format(current_page=page_number,
                                             total_pages=total_pages,
                                             line_number=line_number,
                                             total_lines=total_lines,
                                             content_char_count=content_char_count,
                                             total_char_count=total_char_count)
        ##<!-- PLC: Page:{page_number}/{total_pages}, Line:{line_number}/{total_lines}, Chars:{content_char_count}/{total_char_count} -->"
        result_lines.append(injected_title)
        result_lines.extend(content_lines)

    return '\n'.join(result_lines)
