"""
页面处理相关的数据类型定义
"""

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class PageAction:
    """页面处理动作"""
    action_type: str  # 动作类型，如 'remove_header', 'fix_heading', 'merge_table'
    line_start: int  # 起始行（1-based）
    line_end: int    # 结束行（1-based）
    params: Dict = field(default_factory=dict)  # 额外参数

@dataclass
class PageAnalysisResult:
    """页面分析结果"""
    # 简单模式匹配结果（如页眉页脚模式）
    simple_patterns: Dict[str, List[str]] = field(default_factory=dict)
    
    # LLM分析结果（如标题层级、表格关系等）
    llm_analyzed: Dict = field(default_factory=dict)
    
    # 每个页面的处理动作
    page_actions: Dict[int, List[PageAction]] = field(default_factory=dict) 