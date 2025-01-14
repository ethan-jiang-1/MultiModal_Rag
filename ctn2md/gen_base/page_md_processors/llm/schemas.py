"""
LLM分析结果的数据模型定义

核心设计思路：
1. 完整性优先：确保不遗漏任何可能的标题
2. 位置精确：通过页号和行号准确定位
3. 保留上下文：维护必要的关联信息
4. 支持后处理：预留足够的扩展空间
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class HeadingInfo(BaseModel):
    """标题信息 - 捕获所有可能的标题
    
    设计考虑：
    1. 完整性优先于准确性
    2. 保留原始信息供后续处理
    3. 精确定位支持后续查找
    4. 初步层级供后续参考
    """
    page: int = Field(..., description="标题所在页号，用于定位和关联")
    line: int = Field(..., description="标题所在行号，用于精确定位")
    content: str = Field(..., description="标题原始内容，保持完整性")
    level: int = Field(ge=1, le=6, description="初步推测的标题层级(1-6)")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="标题判断的置信度")
    format_hints: Optional[List[str]] = Field(default_factory=list, description="标题格式特征列表")

class TableRange(BaseModel):
    """表格范围 - 精确定位表格位置
    
    设计考虑：
    1. 精确定位表格边界
    2. 识别表格组成部分
    3. 支持跨页处理
    """
    start: int = Field(..., description="起始行号")
    end: int = Field(..., description="结束行号")
    has_header: bool = Field(default=False, description="是否包含表头")

class MergeAction(BaseModel):
    """合并动作 - 处理跨页内容
    
    设计考虑：
    1. 支持多种合并类型
    2. 精确定位合并范围
    3. 维护页面关系
    """
    type: str = Field(..., description="合并类型(table)")
    pages: List[int] = Field(..., description="涉及的页面列表")
    line_ranges: Dict[str, List[TableRange]] = Field(..., description="每页的行范围")

class RemoveAction(BaseModel):
    """删除动作 - 处理冗余内容
    
    设计考虑：
    1. 精确定位删除位置
    2. 明确删除原因
    3. 支持批量操作
    """
    page: int = Field(..., description="页号")
    lines: List[int] = Field(..., description="需要删除的行号列表")
    reason: str = Field(..., description="删除原因(header/footer)")

class DocumentAnalysis(BaseModel):
    """文档分析结果 - 整合所有分析信息
    
    设计考虑：
    1. 标题信息优先：放在最前面强调重要性
    2. 完整性保证：包含所有必要信息
    3. 结构化组织：便于后续处理
    4. 可扩展性：支持添加新的分析结果
    """
    heading_infos: List[HeadingInfo] = Field(
        default_factory=list, 
        description="标题信息列表 - 包含所有可能的标题"
    )
    remove_actions: List[RemoveAction] = Field(
        default_factory=list, 
        description="删除动作列表 - 处理页眉页脚等"
    )
    merge_actions: List[MergeAction] = Field(
        default_factory=list, 
        description="合并动作列表 - 处理跨页表格等"
    ) 