"""
页面处理器的基类和通用工具函数
"""

import os
import logging
import shutil
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo

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
        src_path = os.path.join(md_info.get_out_dir(), src_path)
        dst_path = os.path.join(workspace_dir, os.path.basename(src_path))
        shutil.copy2(src_path, dst_path)
        workspace_files.append(dst_path)
        
    return workspace_files

def read_page_content(page_path: str) -> List[str]:
    """读取页面内容"""
    try:
        with open(page_path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]
    except Exception as e:
        logger.error(f"Error reading page {page_path}: {e}")
        return []

def save_page_content(page_path: str, content: List[str]) -> bool:
    """保存页面内容"""
    try:
        with open(page_path, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line + '\n')
        return True
    except Exception as e:
        logger.error(f"Error saving page {page_path}: {e}")
        return False

def load_pages_content(page_paths: List[str]) -> List[List[str]]:
    """加载所有页面内容
    
    Args:
        page_paths: 页面文件路径列表
        
    Returns:
        所有页面的内容列表
    """
    pages_content = []
    for path in page_paths:
        content = read_page_content(path)
        if content:
            pages_content.append(content)
    return pages_content

def save_pages_content(page_paths: List[str], pages_content: List[List[str]]) -> bool:
    """保存所有页面内容
    
    Args:
        page_paths: 页面文件路径列表
        pages_content: 所有页面的内容列表
        
    Returns:
        是否全部保存成功
    """
    if len(page_paths) != len(pages_content):
        logger.error("Page paths and content count mismatch")
        return False
        
    success = True
    for path, content in zip(page_paths, pages_content):
        if not save_page_content(path, content):
            success = False
    return success

class BaseProcessor:
    """处理器基类"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象,包含文档相关的配置和上下文信息
        """
        self.md_info = md_info
        
    def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
        """处理页面内容
        
        Args:
            pages: 所有页面的内容
            actions: LLM分析得到的动作指令
            
        Returns:
            处理后的页面内容
        """
        raise NotImplementedError 

if __name__ == "__main__":
    import rich
    from dotenv import load_dotenv
    load_dotenv()
    
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试代码
    from ctn2md.md_info.md_info_base import MdInfo
    
    # 创建测试目录
    test_dir = "_output/test_base"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试文件
    test_file = os.path.join(test_dir, "test.md")
    test_content = ["测试行1", "测试行2", "测试行3"]
    save_page_content(test_file, test_content)
    
    # 测试读取
    loaded_content = read_page_content(test_file)
    print("读取的内容:", loaded_content)
    
    # 测试工作空间准备
    pname_info = "_work/ctn2md_mrag__1__座椅STO间隙_P1_lp/_info.json"
    # 测试MD融合工作空间准备
    md_info = MdInfo(pname_info)
    workspace_files = prepare_md_fusion_workspace(md_info)
    rich.print("工作空间文件:", workspace_files) 