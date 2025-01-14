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

class TableRange(BaseModel):
    """表格范围 - 精确定位表格位置
    
    设计考虑：
    1. 精确定位表格边界
    2. 识别表格组成部分
    3. 支持跨页处理
    """
    start: int = Field(..., description="起始行号")
    end: int = Field(..., description="结束行号")
    content_type: str = Field(..., description="内容类型(table_header/table_body)")

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
    confidence: float = Field(..., ge=0.0, le=1.0, description="合并判断的置信度")
    notes: Optional[str] = Field(None, description="额外说明")

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
    confidence: float = Field(..., ge=0.0, le=1.0, description="删除判断的置信度")
    pattern: Optional[str] = Field(None, description="匹配的模式")
    notes: Optional[str] = Field(None, description="额外说明")

class Warning(BaseModel):
    """警告信息 - 记录不确定的判断
    
    设计考虑：
    1. 明确警告类型
    2. 精确定位位置
    3. 提供详细说明
    """
    type: str = Field(..., description="警告类型")
    page: int = Field(..., description="页号")
    lines: List[int] = Field(..., description="相关行号列表")
    message: str = Field(..., description="警告信息")

class PageDebugInfo(BaseModel):
    """页面调试信息 - 记录页面基本统计数据
    
    设计考虑：
    1. 页面完整性验证
    2. 行号范围确认
    3. 内容边界检查
    """
    page: int = Field(..., description="页号")
    total_lines: int = Field(..., description="总行数")
    first_line: str = Field(..., description="第一行内容")
    last_line: str = Field(..., description="最后一行内容")

class DocumentDebugInfo(BaseModel):
    """文档调试信息 - 记录文档整体统计数据
    
    设计考虑：
    1. 文档完整性验证
    2. 页面数量确认
    3. 支持分页分析
    """
    total_pages: int = Field(..., description="总页数")
    pages: List[PageDebugInfo] = Field(..., description="各页面信息")

class DocumentAnalysis(BaseModel):
    """文档分析结果 - 整合所有分析信息
    
    设计考虑：
    1. 完整性保证：包含所有必要信息
    2. 结构化组织：便于后续处理
    3. 可扩展性：支持添加新的分析结果
    """
    debug_info: DocumentDebugInfo = Field(
        ...,
        description="调试信息 - 记录文档基本统计数据"
    )
    remove_actions: List[RemoveAction] = Field(
        default_factory=list, 
        description="删除动作列表 - 处理页眉页脚等"
    )
    merge_actions: List[MergeAction] = Field(
        default_factory=list, 
        description="合并动作列表 - 处理跨页表格等"
    )
    warnings: List[Warning] = Field(
        default_factory=list,
        description="警告列表 - 记录不确定的判断"
    ) 