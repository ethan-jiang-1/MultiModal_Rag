"""
页面MD处理器模块

提供一系列处理器用于分析和处理分页MD文档：
- 内容分析
- 页眉页脚处理
- 标题层级处理
- 表格合并处理
- 动作执行
"""

from .base import BaseProcessor
from .data_types import PageAnalysisResult, PageAction
from .content_analyzer import ContentAnalyzer
from .header_footer import HeaderFooterProcessor
from .heading_hierarchy import HeadingHierarchyProcessor
from .table_merger import TableMergerProcessor
from .action_executor import ActionExecutor

__all__ = [
    # 基础类
    'BaseProcessor',
    
    # 数据类型
    'PageAnalysisResult',
    'PageAction',
    
    # 处理器
    'ContentAnalyzer',
    'HeaderFooterProcessor',
    'HeadingHierarchyProcessor',
    'TableMergerProcessor',
    'ActionExecutor',
] 