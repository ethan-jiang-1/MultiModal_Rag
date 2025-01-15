"""
Data Models for LLM Analysis Results

Core Design Principles:
1. Completeness First: Ensure no potential headings are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

from typing import List, Dict, Optional, Union
import os
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class TableRange(BaseModel):
    """表格范围 - 定位表格在页面中的位置
    
    Attributes:
        start: 起始行号(1-based)
        end: 结束行号(1-based)
        is_header: 是否为表头部分
        has_separator: 是否包含分隔符行(---)
    """
    start: int = Field(..., description="起始行号(1-based)")
    end: int = Field(..., description="结束行号(1-based)")
    is_header: bool = Field(default=False, description="是否为表头部分")
    has_separator: bool = Field(default=False, description="是否包含分隔符行(---)")

class MergeAction(BaseModel):
    """合并动作 - 描述需要合并的内容
    
    Attributes:
        type: 合并类型，默认为"table"
        pages: 涉及的页码列表
        line_ranges: 每页的行范围
        confidence: 置信度(0.0-1.0)
        is_cross_page: 是否确实需要跨页合并
        table_structure: 表格结构信息
    """
    type: str = "table"
    pages: List[int]
    line_ranges: Dict[str, List[TableRange]]
    confidence: float
    is_cross_page: bool = Field(default=False, description="是否确实需要跨页合并")
    table_structure: Optional[Dict[str, Union[int, bool]]] = Field(default=None, description="表格结构信息，包含columns和has_header")

class RemoveAction(BaseModel):
    """删除动作 - 描述需要删除的内容
    
    Attributes:
        page: 页码
        lines: 行号列表
        reason: 删除原因
        confidence: 置信度(0.0-1.0)
    """
    page: int
    lines: List[int]
    reason: str
    confidence: float

class Warning(BaseModel):
    """警告信息 - 记录处理过程中的异常情况
    
    Attributes:
        type: 警告类型
        page: 页码
        lines: 相关行号
        message: 警告信息
    """
    type: str
    page: int
    lines: List[int]
    message: str

class PageDebugInfo(BaseModel):
    """页面调试信息 - 记录单页的统计数据
    
    Attributes:
        page: 页码
        total_lines: 总行数
        heading_count: 标题数量
        table_count: 表格数量
        image_count: 图片数量
        first_line_preview: 首行预览(前32字符)
        last_line_preview: 末行预览(前32字符)
    """
    page: int
    total_lines: int
    heading_count: int = Field(description="标题数量")
    table_count: int = Field(description="表格数量")
    image_count: int = Field(description="图片数量")
    first_line_preview: str = Field(description="首行预览(前32字符)")
    last_line_preview: str = Field(description="末行预览(前32字符)")

class DocumentDebugInfo(BaseModel):
    """文档调试信息 - 记录整体统计数据
    
    Attributes:
        total_pages: 总页数
        pages: 每页的调试信息
    """
    total_pages: int
    pages: List[PageDebugInfo]

class DocumentAnalysis(BaseModel):
    """文档分析结果 - 整合所有分析信息
    
    Attributes:
        debug_info: 调试信息
        remove_actions: 删除动作列表
        merge_actions: 合并动作列表
        warnings: 警告信息列表
    """
    debug_info: DocumentDebugInfo
    remove_actions: Optional[List[RemoveAction]] = []
    merge_actions: Optional[List[MergeAction]] = []
    warnings: Optional[List[Warning]] = []

if __name__ == "__main__":
    # 确保在项目根目录下运行
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试数据
    test_doc = {
        "debug_info": {
            "total_pages": 2,
            "pages": [
                {
                    "page": 1,
                    "total_lines": 20,
                    "heading_count": 2,
                    "table_count": 1,
                    "image_count": 0,
                    "first_line_preview": "[P1-L1] # Title",
                    "last_line_preview": "[P1-L20] End of page"
                }
            ]
        },
        "merge_actions": [
            {
                "type": "table",
                "pages": [1, 2],
                "line_ranges": {
                    "1": [
                        {
                            "start": 10,
                            "end": 15,
                            "is_header": True,
                            "has_separator": True
                        }
                    ]
                },
                "confidence": 0.95,
                "is_cross_page": True
            }
        ]
    }
    
    # 验证文档
    result = DocumentAnalysis.model_validate(test_doc)
    print("Valid document analysis:", result)
    
    # 测试无效文档
    invalid_doc = {
        "debug_info": {
            "total_pages": 1,
            "pages": ["invalid page info"]  # 应该导致验证错误
        }
    }
    try:
        DocumentAnalysis.model_validate(invalid_doc)
    except Exception as e:
        print("Expected validation error:", e) 