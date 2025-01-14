"""
表格合并处理器
"""

from typing import List, Dict, Tuple
import logging

from ctn2md.gen_base.page_md_processors.base import BaseProcessor
from ctn2md.src.md_info_base import MdInfo

logger = logging.getLogger(__name__)

class TableMergerProcessor(BaseProcessor):
    """表格合并处理器：负责处理跨页表格"""
    
    def process(self, current_content: List[str], next_content: List[str], llm_analyzed: Dict) -> Tuple[List[str], List[str]]:
        """处理跨页表格
        
        Args:
            current_content: 当前页面内容
            next_content: 下一页面内容
            llm_analyzed: LLM分析结果,包含表格信息
            
        Returns:
            处理后的当前页面和下一页面内容
        """
        # TODO: 实现表格合并逻辑
        return current_content, next_content

if __name__ == "__main__":
    # 设置日志
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试处理器
    json_path = "_output/ctn2md_mrag__AIGC时代的人力资源管理进化(徐刚)_lvlm/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    # 准备工作空间
    from .base import prepare_md_fusion_workspace, read_page_content, save_page_content
    pages = prepare_md_fusion_workspace(md_info)
    
    # 初始化处理器
    processor = TableMergerProcessor(md_info)
    
    # 测试处理
    llm_analyzed = {
        "tables": [
            {
                "start_page": 0,
                "end_page": 1,
                "columns": 3
            }
        ]
    }
    
    # 处理相邻页面
    for i in range(len(pages) - 1):
        current_content = read_page_content(pages[i])
        next_content = read_page_content(pages[i + 1])
        if current_content and next_content:
            # 处理表格
            new_current, new_next = processor.process(current_content, next_content, llm_analyzed)
            # 保存更新后的内容
            save_page_content(pages[i], new_current)
            save_page_content(pages[i + 1], new_next) 