"""
LLM分析结果的数据模型定义
"""

from typing import List, Dict
from pydantic import BaseModel, Field

class RemoveAction(BaseModel):
    """删除动作"""
    page: int = Field(..., description="页号")
    lines: List[int] = Field(..., description="需要删除的行号列表")
    reason: str = Field(..., description="删除原因（页眉/页脚）")

class TableRange(BaseModel):
    """表格范围"""
    start: int = Field(..., description="起始行号")
    end: int = Field(..., description="结束行号")

class MergeAction(BaseModel):
    """合并动作"""
    type: str = Field(..., description="合并类型（table等）")
    pages: List[int] = Field(..., description="涉及的页面列表")
    line_ranges: Dict[str, List[TableRange]] = Field(..., description="每页的行范围")

class DocumentAnalysis(BaseModel):
    """文档分析结果"""
    remove_actions: List[RemoveAction] = Field(default_factory=list, description="删除动作列表")
    merge_actions: List[MergeAction] = Field(default_factory=list, description="合并动作列表") 