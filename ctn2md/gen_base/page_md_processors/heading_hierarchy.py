"""
标题层级处理器
"""

from typing import List, Dict
import logging

from ctn2md.gen_base.page_md_processors.base import BaseProcessor
from ctn2md.src.md_info_base import MdInfo

logger = logging.getLogger(__name__)

class HeadingHierarchyProcessor(BaseProcessor):
    """标题层级处理器：负责重建标题的层级关系"""
    
    def process(self, page_content: List[str], llm_analyzed: Dict) -> List[str]:
        """处理标题层级
        
        Args:
            page_content: 页面内容行列表
            llm_analyzed: LLM分析结果,包含标题层级信息
            
        Returns:
            处理后的页面内容行列表
        """
        # TODO: 实现标题层级处理逻辑
        return page_content

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
    processor = HeadingHierarchyProcessor(md_info)
    
    # 测试处理
    llm_analyzed = {
        "headings": [
            {"text": "第一章", "level": 1},
            {"text": "1.1 节", "level": 2}
        ]
    }
    
    # 处理每个页面
    for page in pages:
        content = read_page_content(page)
        if content:
            # 处理标题层级
            new_content = processor.process(content, llm_analyzed)
            # 保存更新后的内容
            save_page_content(page, new_content) 