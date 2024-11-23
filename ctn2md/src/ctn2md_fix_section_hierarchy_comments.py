from dotenv import load_dotenv
import os
import sys
import logging
import rich
import shutil
import re
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
    在 Markdown 文本的每个标题前插入基于层级的描述注释，并记录分割情况。

    :param md_text: 原始 Markdown 文本
    :param md_info: 已存在的字典，用于记录描述注释信息
    :return: 带描述注释的 Markdown 文本和更新后的 md_info
    """
    lines = md_text.strip().split('\n')
    processed_lines = []
    hierarchy_stack = []  # 用于维护标题的层级
    doc_title = None  # 当前的一级标题
    md_info["sections"] = {}

    for line in lines:
        # 检测是否是标题行
        if line.startswith("#"):
            level = line.count("#")  # 根据 # 的数量确定标题层级
            title = line[level:].strip()  # 提取标题内容

            # 如果是一级标题，更新文档标题
            if level == 1:
                doc_title = title  # 设置新的一级标题
                hierarchy_stack = []  # 清空层级堆栈
                # 确保 doc_title 在 md_info 中存在
                if doc_title not in md_info["sections"]:
                    md_info["sections"][doc_title] = []  # 初始化该 doc_title 的记录
            else:
                # 调整堆栈以匹配当前标题的层级
                while len(hierarchy_stack) >= level - 1:
                    hierarchy_stack.pop()
                hierarchy_stack.append(title)  # 添加当前标题到堆栈

            # 生成描述信息
            # 清理标题和层级堆栈
            clean_doc_title = re.sub(r'\s+', ' ', doc_title).strip()
            clean_hierarchy_stack = [re.sub(r'\s+', ' ', title).strip() for title in hierarchy_stack]

            # 生成安全的 hierarchy_desc 和 desc
            hierarchy_desc = f"{clean_doc_title} __ {' __ '.join(clean_hierarchy_stack)}"
            desc = f"<!-- [desc] {hierarchy_desc} [desc] -->"

            # 记录到 md_info
            md_info["sections"][doc_title].append(hierarchy_desc)

            # 插入描述注释
            processed_lines.append("")
            processed_lines.append(desc)

        # 无论是否是标题行，都保留原始行
        processed_lines.append(line)

    # 将处理后的内容重新组合为 Markdown 文本
    return "\n".join(processed_lines)

def truncate_name(name, max_length=16):
    """
    截断名称，限制长度为 max_length，超长时用 '--' 表示省略。
    """
    if len(name) <= max_length:
        return name
    return f"{name[:4]}--{name[-4:]}"


def split_markdown_to_files_with_desc_and_sequence(markdown_text, output_dir):
    """
    将带有 `<!-- [desc] ... [desc] -->` 标记的 Markdown 文本切割为多个部分，
    保存到指定目录，并为文件名添加序号和截断描述。

    :param markdown_text: 带有描述标记的 Markdown 文本
    :param output_dir: 输出目录路径
    """
    os.makedirs(output_dir, exist_ok=True)

    lines = markdown_text.strip().split('\n')
    current_section = []
    current_desc = None
    file_index = 0  # 用于生成序号

    for line in lines:
        # 检测描述标记
        if line.startswith("<!-- [desc]") and line.endswith("[desc] -->"):
            # 如果已有 section，保存到文件
            if current_section and current_desc:
                file_index += 1
                clean_desc = re.sub(r'\s+', ' ', current_desc).strip()
                safe_desc = "__".join(
                    truncate_name(part.strip(), max_length=16)
                    for part in clean_desc.split(" __ ")
                )
                file_name = f"{file_index:04d}_{safe_desc}.md"
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"[desc] {clean_desc} [/desc]\n")
                    file.write("\n".join(current_section))
                current_section = []  # 重置当前 section

            # 提取描述内容并清理换行符
            current_desc = re.sub(r'\s+', ' ', line[len("<!-- [desc] "):-len(" [desc] -->")]).strip()
        else:
            # 收集当前 section 的内容
            current_section.append(line)

    # 保存最后一个 section
    if current_section and current_desc:
        file_index += 1
        clean_desc = re.sub(r'\s+', ' ', current_desc).strip()
        safe_desc = "__".join(
            truncate_name(part.strip(), max_length=16)
            for part in clean_desc.split(" __ ")
        )
        file_name = f"{file_index:04d}_{safe_desc}.md"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"[desc] {clean_desc} [/desc]\n")
            file.write("\n".join(current_section))

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

    pathname_sections = os.path.join(os.path.dirname(md_info.get_md_info_path()), "sections") 
    md_info["sections_output_dir"] = pathname_sections
    if os.path.isdir(pathname_sections):
        shutil.rmtree(pathname_sections)
    os.makedirs(pathname_sections, exist_ok=True)
    split_markdown_to_files_with_desc_and_sequence(md_text_new, pathname_sections)
    
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