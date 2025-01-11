"""
标题更新模块
负责根据映射更新文档内容
"""
import copy
import logging
from typing import Tuple
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo

def update_markdown_heading_content(md_text: str, md_info: MdInfo, fhl_map: dict) -> Tuple[str, list]:
    """
    替换 Markdown 文本中的标题内容，根据 fhl_map 提供的替换规则。

    参数:
        md_text: Markdown 文本
        md_info: Markdown 文件的基本信息
        fhl_map: 包含映射规则的 JSON 字典
    返回:
        Tuple[str, list]: (替换后的 Markdown 文本, 未处理的 fhl_map 副本)
    """
    fname_org_doc = md_info.get("fname_org_doc", "unknown")
    
    fhl_map_copy = copy.deepcopy(fhl_map)
    heading_lines_map = fhl_map_copy.get("optimized_heading_lines_map", [])
    
    if len(heading_lines_map) == 0:
        logging.error(f"Empty heading_lines_map for {fname_org_doc}")
        raise ValueError("UMHC: heading_lines_map == [] ?!")

    lines = md_text.splitlines()
    new_lines = []
    used_indices = set()

    # 处理标题替换
    for line in lines:
        stripped_line = line.strip()
        replaced = False

        if stripped_line.startswith("#"):
            for i, item in enumerate(heading_lines_map):
                if i in used_indices:
                    continue
                if stripped_line.startswith(item["original_line"]):
                    new_line = item["mapped_line"] or ""
                    new_lines.append(new_line)
                    used_indices.add(i)
                    replaced = True
                    break

        if not replaced:
            new_lines.append(line)

    # 只在有未处理项时记录警告
    unprocessed_heading_lines_map = [
        item for i, item in enumerate(heading_lines_map) if i not in used_indices
    ]
    if unprocessed_heading_lines_map:
        logging.warning(f"Found {len(unprocessed_heading_lines_map)} unprocessed headings in {fname_org_doc}")

    return "\n".join(new_lines), unprocessed_heading_lines_map
