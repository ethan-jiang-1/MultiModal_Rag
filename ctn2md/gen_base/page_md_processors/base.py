"""
页面处理器的基类和通用工具函数
"""

import os
import logging
import shutil
from typing import List
from dotenv import load_dotenv

load_dotenv()

from ctn2md.src.md_info_base import MdInfo

logger = logging.getLogger(__name__)

def prepare_md_fusion_workspace(md_info: MdInfo) -> List[str]:
    """准备MD融合的工作空间
    
    Args:
        md_info: MD信息对象
        
    Returns:
        工作目录中的文件路径列表
    """
    # 1. 获取工作目录
    workspace_dir = md_info.get_aux_md_fusion_dir()
    
    # 2. 准备工作空间
    os.makedirs(workspace_dir, exist_ok=True)
    
    # 3. 复制文件
    workspace_files = []
    for src_path in md_info.get_fnames_pages():
        dst_path = os.path.join(workspace_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)
        workspace_files.append(dst_path)
        
    return workspace_files

def read_page_content(page_path: str) -> List[str]:
    """读取页面内容
    
    Args:
        page_path: 页面文件路径
        
    Returns:
        页面内容行列表
    """
    try:
        with open(page_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        logger.error(f"Error reading page {page_path}: {e}")
        return []

def save_page_content(page_path: str, content: List[str]) -> bool:
    """保存页面内容
    
    Args:
        page_path: 页面文件路径
        content: 要保存的内容行列表
        
    Returns:
        是否保存成功
    """
    try:
        with open(page_path, 'w', encoding='utf-8') as f:
            f.writelines(content)
        return True
    except Exception as e:
        logger.error(f"Error saving page {page_path}: {e}")
        return False

class BaseProcessor:
    """处理器基类"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象,包含文档相关的配置和上下文信息
        """
        self.md_info = md_info 