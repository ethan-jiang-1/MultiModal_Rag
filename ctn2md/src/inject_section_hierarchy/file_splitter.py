"""
文件分割模块
负责处理文件的分割、保存和清理操作
"""
import os
import re
import logging
from typing import List, Tuple

from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.utils.util_file import get_crc32_id

ORDERD_NO_HEADING = "0_NoHeading"

def clear_section_files(output_dir: str):
    """
    清理指定目录下的所有分段文件（以 xcs_ 开头的 .md 文件）
    
    :param output_dir: 输出目录路径
    """
    if not os.path.isdir(output_dir):
        return 

    # 正则模式：匹配以 xcs_ 开头，然后跟任何字符串，最后.md 结尾的文件名
    pattern = re.compile(r'^xcs_.*\.md$')

    names = os.listdir(output_dir)
    for name in names:
        # 检查是否符合正则模式
        if pattern.match(name):
            file_path = os.path.join(output_dir, name)
            try:
                os.remove(file_path)
                logging.info(f"Deleted: {file_path}")
            except Exception as e:
                logging.exception(f"Failed to delete {file_path}: {e}")

def _extract_ordered_and_desc(line: str) -> Tuple[str, str]:
    """
    从一行中提取 ordered_name 和 desc 的内容。
    :param line: 包含注释的 Markdown 行
    :return: (ordered_name, desc) 或 (None, None) 如果未找到
    """
    try:
        # 提取 [ordered_name] 和 [desc] 使用单个正则表达式匹配整个结构
        pattern = r'<!--\s*\[ordered_name\]\s*(.+?)\s*\[ordered_name\]\s*\[desc\]\s*(.+?)\s*\[desc\]\s*-->'
        match = re.search(pattern, line)
        
        if match:
            ordered_name = match.group(1)
            desc = match.group(2)
            return ordered_name, desc
        
        # 如果不匹配，返回 None, None
        return None, None
    except Exception as e:
        logging.error(f"Error extracting from line: {line}")
        logging.exception(e)
        return None, None

def _save_section_to_file(output_dir:str, file_index:int, ordered_name:str, desc:str, section_content:str, crc32_id:str)-> str:
    """
    将一个 Markdown 段落保存到文件。
    :param output_dir: 输出目录路径
    :param file_index: 当前文件索引
    :param ordered_name: 当前段落的 ordered_name
    :param desc: 当前段落的 desc
    :param section_content: 当前段落的完整内容
    :return: str 生成的文件名
    """
    try:
        # 安全处理文件名
        safe_ordered_name = re.sub(r'\)', '-', ordered_name, count=1)
        safe_ordered_name = re.sub(r'[^\w\-]', '_', safe_ordered_name)  # 非字母、数字、下划线或连字符的字符替换为下划线
        file_name = f"xcs_{crc32_id}_{file_index:04d}_{safe_ordered_name}.md"
        file_path = os.path.join(output_dir, file_name)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            if desc:
                f.write(f"<!-- [desc] {desc} [desc] -->\n")
            if ordered_name == ORDERD_NO_HEADING:
                f.write(f"<!-- [ordered_name] 0) {ORDERD_NO_HEADING} [ordered_name] [desc] {desc} [desc] -->")
            f.write(section_content)

        logging.info(f"Saved section to file: {file_path}")
        return file_name
    except Exception as e:
        logging.error(f"Error saving section to file: {file_name}")
        logging.exception(e)
        return None

def _save_current_section(output_dir:str, file_index:int, created_filenames:List[str], 
                         section_content:str, ordered_name:str, desc:str, 
                         saved_no_ordered_name:str, crc32_id:str) -> int:
    """
    保存当前段落到文件。

    :param output_dir: 输出目录路径
    :param file_index: 当前文件索引
    :param created_filenames: 已创建文件名列表
    :param section_content: 要保存的段落内容
    :param ordered_name: 段落的 ordered_name 或 None
    :param desc: 段落的 desc 或 None
    :param saved_no_ordered_name: 是否已保存无 ordered_name 的段落
    :return: 更新后的文件索引
    """
    if not section_content.strip():
        return file_index  # 跳过空内容

    if not ordered_name and not saved_no_ordered_name:
        # 保存无 ordered_name 的段落
        file_name = _save_section_to_file(
            output_dir=output_dir,
            file_index=0,
            ordered_name=ORDERD_NO_HEADING,
            desc="NoDescription",
            section_content=section_content,
            crc32_id=crc32_id
        )
        created_filenames.append(file_name)
    elif ordered_name:
        # 保存有 ordered_name 的段落
        file_name = _save_section_to_file(
            output_dir=output_dir,
            file_index=file_index,
            ordered_name=ordered_name,
            desc=desc or "NoDescription",
            section_content=section_content,
            crc32_id=crc32_id
        )
        created_filenames.append(file_name)
        file_index += 1

    return file_index

def split_sections_to_files(markdown_text:str, md_info:MdInfo) -> List[str]:
    """
    将带有 `<!-- [ordered_name] ... [ordered_name] [desc] ... [desc] -->` 标记的 Markdown 文本
    切割为多个部分，保存到指定目录，并使用 `ordered_name` 作为文件名（在前面加上4位递增的数字作为前缀，再跟上一个 `_`）。
    
    :param markdown_text: 带有描述标记的 Markdown 文本
    :param output_dir: 输出目录路径
    :return: list[str] 所有新生成的文件名
    """
    output_dir = md_info.get_out_dir()
    os.makedirs(output_dir, exist_ok=True)
    
    crc32_id = get_crc32_id(md_info.get_doc_pathname())

    # 分割 Markdown 行
    lines = markdown_text.strip().split('\n')
    current_section = []
    current_ordered_name = None
    current_desc = None
    created_filenames = []  # 用于存储所有生成的文件名

    # 文件索引：0 用于无 `ordered_name` 的内容，1 开始用于有 `ordered_name` 的内容
    file_index = 1
    saved_no_ordered_name = False

    for line in lines:
        # 检测 `ordered_name` 和 `desc`
        ordered_name, desc = _extract_ordered_and_desc(line)

        if ordered_name:
            # 保存之前的段落
            file_index = _save_current_section(
                output_dir=output_dir,
                file_index=file_index,
                created_filenames=created_filenames,
                section_content="\n".join(current_section),
                ordered_name=current_ordered_name,
                desc=current_desc,
                saved_no_ordered_name=saved_no_ordered_name,
                crc32_id=crc32_id
            )
            saved_no_ordered_name = saved_no_ordered_name or not current_ordered_name
            current_section = []  # 清空段落内容

            # 更新当前 `ordered_name` 和 `desc`
            current_ordered_name = ordered_name
            current_desc = desc

        # 将当前行归入段落内容
        current_section.append(line)

    # 保存最后一个段落
    _save_current_section(
        output_dir=output_dir,
        file_index=file_index,
        created_filenames=created_filenames,
        section_content="\n".join(current_section),
        ordered_name=current_ordered_name,
        desc=current_desc,
        saved_no_ordered_name=saved_no_ordered_name,
        crc32_id=crc32_id
    )

    return created_filenames 