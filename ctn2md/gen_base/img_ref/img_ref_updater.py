from typing import List, Dict
import re
from dotenv import load_dotenv
load_dotenv()

from ctn2md.gen_base.img_ref.models import ImageReference, IMG_REF_PATTERN
from ctn2md.src.md_info_base import MdInfo

def _read_markdown_file(file_path: str) -> str:
    """读取markdown文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def _save_markdown_file(file_path: str, content: str) -> None:
    """保存markdown文件内容"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _build_reference_map(references: List[ImageReference]) -> Dict[str, ImageReference]:
    """构建图片引用映射表
    
    Args:
        references: 图片引用列表
        
    Returns:
        Dict[str, ImageReference]: 以ref_name为key的映射表
    """
    return {ref.ref_name: ref for ref in references}

def _format_image_reference(ref: ImageReference) -> str:
    """格式化图片引用为markdown格式
    
    Args:
        ref: 图片引用信息
        
    Returns:
        str: markdown格式的图片引用
    """
    # 如果figure_name为空，使用ref_name
    figure_name = ref.figure_name if ref.figure_name else ref.ref_name
    
    # 如果有description，添加到引用中
    if ref.image_description:
        return f'![{figure_name}]({ref.ref_name} "{ref.image_description}")'
    else:
        return f'![{figure_name}]({ref.ref_name})'

def _update_markdown_content(content: str, ref_map: Dict[str, ImageReference]) -> str:
    """更新markdown内容中的图片引用
    
    Args:
        content: markdown内容
        ref_map: 图片引用映射表
        
    Returns:
        str: 更新后的markdown内容
    """
    def replace_match(match: re.Match) -> str:
        # 提取图片文件名
        ref_name = match.group(2)
        
        # 在映射表中查找对应的引用信息
        if ref_name in ref_map:
            return _format_image_reference(ref_map[ref_name])
        
        # 如果找不到对应的引用信息，保持原样
        return match.group(0)
    
    # 使用正则表达式替换所有图片引用
    return re.sub(IMG_REF_PATTERN, replace_match, content)

def update_img_ref(md_info: MdInfo, references: List[ImageReference], pname_md_step0: str) -> None:
    """更新markdown文件中的图片引用
    
    Args:
        md_info: MdInfo对象
        references: 更新后的图片引用列表
        pname_md_step0: markdown文件路径
    """
    try:
        # 读取markdown文件
        content = _read_markdown_file(pname_md_step0)
        
        # 构建引用映射表
        ref_map = _build_reference_map(references)
        
        # 更新内容
        updated_content = _update_markdown_content(content, ref_map)
        
        # 保存更新后的内容
        _save_markdown_file(pname_md_step0, updated_content)
        
    except Exception as e:
        # 这里可以添加日志记录
        raise Exception(f"Failed to update image references: {str(e)}")