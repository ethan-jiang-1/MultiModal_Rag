"""
Data Models for LLM Analysis Results

Core Design Principles:
1. Completeness First: Ensure no potential headings are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

from typing import List, Optional
import os
from enum import Enum
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()

# Base Enums
class HeadingErrorType(str, Enum):
    """Error types for heading validation"""
    WRONG_LEVEL = "wrong_level"      # 是标题但层次错误
    NEEDS_LEVEL = "needs_level"      # 应该是标题但没有层次
    NOT_HEADING = "not_heading"      # 被误认为是标题但实际是正文
    MISSING = "missing"              # 标题缺失（根据上下文推断）
    WRONG_FORMAT = "wrong_format"    # 标题格式错误（如编号问题）
    INCONSISTENT = "inconsistent"    # 与文档结构不一致

class HeadingValidationScope(str, Enum):
    """Validation scope for heading analysis"""
    SINGLE_PAGE = "single_page"      # 单页内验证
    CROSS_PAGE = "cross_page"        # 跨页验证
    DOCUMENT = "document"            # 整个文档范围验证

class HeadingRemoveReason(str, Enum):
    """Removal reason enumeration"""
    HEADER = "header"                # 页眉
    FOOTER = "footer"                # 页脚
    DUPLICATE = "duplicate"          # 重复内容
    NOISE = "noise"                  # 噪声内容
    SEPARATOR = "separator"          # 分隔线

class HeadingWarningType(str, Enum):
    """Warning type enumeration"""
    STRUCTURE = "structure"          # 结构问题
    CROSS_PAGE = "cross_page"        # 跨页问题
    INCONSISTENT = "inconsistent"    # 不一致问题
    AMBIGUOUS = "ambiguous"          # 模糊不清
    FORMAT = "format"                # 格式问题

class HeadingFormatFeature(str, Enum):
    """格式特征"""
    NUMBER_FORMAT = "number_format"   # 编号格式
    INDENT = "indent"                # 缩进
    EMPTY_LINES = "empty_lines"      # 空行
    FONT_STYLE = "font_style"        # 字体样式

class HeadingContentFeature(str, Enum):
    """内容特征"""
    LENGTH = "length"                # 长度
    KEYWORDS = "keywords"            # 关键词
    TOPIC = "topic"                  # 主题类型

class HeadingContextFeature(str, Enum):
    """上下文特征"""
    SECTION_LEVEL = "section_level"   # 章节层级
    CONTENT_FLOW = "content_flow"     # 内容流
    SEQUENCE = "sequence"             # 序列关系

class HeadingPositionFeature(str, Enum):
    """位置特征"""
    PAGE_TOP = "page_top"            # 页面顶部
    PAGE_BOTTOM = "page_bottom"      # 页面底部
    PARAGRAPH_START = "para_start"    # 段落开始
    AFTER_BREAK = "after_break"      # 分隔符后

class HeadingHeaderPattern(str, Enum):
    """页眉模式"""
    TITLE_PAGE = "title_page"          # 标题页
    TITLE_NUMBER = "title_number"      # 标题+页码
    NUMBER_ONLY = "number_only"        # 仅页码
    CHAPTER_TITLE = "chapter_title"    # 章节标题
    CUSTOM = "custom"                  # 自定义模式

class HeadingLevelGapType(str, Enum):
    """层级断层类型"""
    SKIP_LEVEL = "skip_level"          # 跳级
    WRONG_ORDER = "wrong_order"        # 顺序错误
    MIXED_FORMAT = "mixed_format"      # 格式混乱
    INVALID_NESTING = "invalid_nesting" # 嵌套错误

class HeadingCrossPageIssueType(str, Enum):
    """跨页问题类型"""
    BREAK_HEADING = "break_heading"    # 标题断开
    LOST_CONTEXT = "lost_context"      # 上下文丢失
    REPEAT_HEADING = "repeat_heading"  # 标题重复

# Base Data Classes
class _HeadingWarningInfo(BaseModel):
    """警告信息"""
    type: HeadingWarningType
    page: int = Field(gt=0)
    lines: List[int]
    message: str = Field(max_length=200)  # 增加消息长度限制

class _HeadingLevelGapInfo(BaseModel):
    """层级断层信息"""
    type: HeadingLevelGapType
    start_level: int
    end_level: int
    page: int = Field(gt=0)

class _HeadingCrossPageInfo(BaseModel):
    """跨页问题信息"""
    type: HeadingCrossPageIssueType
    start_page: int
    end_page: int
    heading_index: int

class HeadingJudgmentBasis(BaseModel):
    """LLM判断依据"""
    format_features: List[HeadingFormatFeature] = Field(default_factory=list, description="格式特征")
    content_features: List[HeadingContentFeature] = Field(default_factory=list, description="内容特征")
    context_features: List[HeadingContextFeature] = Field(default_factory=list, description="上下文特征")
    position_features: List[HeadingPositionFeature] = Field(default_factory=list, description="位置特征")

class HeadingContext(BaseModel):
    """标题上下文"""
    prev_heading_id: Optional[str] = Field(None, description="前一个标题ID (从1开始的自然数序号的字符串形式)")
    is_cross_page: bool = Field(False, description="是否跨页")

    @field_validator('prev_heading_id')
    def validate_prev_heading_id(cls, v):
        """验证prev_heading_id是否为有效的自然数字符串"""
        if v is None:
            return v
        try:
            num = int(v)
            if num < 1:
                raise ValueError('Previous heading ID must be a positive integer')
        except ValueError:
            raise ValueError('Previous heading ID must be a string representation of a positive integer (e.g., "1", "2", "3")')
        return v

class HeadingValidation(BaseModel):
    """标题验证结果"""
    is_valid: bool = Field(..., description="是否有效")
    current_level: Optional[int] = Field(None, description="当前层级")
    expected_level: Optional[int] = Field(None, description="期望层级")
    error_type: Optional[HeadingErrorType] = Field(None, description="错误类型")
    validation_scope: HeadingValidationScope = Field(..., description="验证范围")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    judgment_basis: Optional[HeadingJudgmentBasis] = Field(None, description="判断依据")
    context: Optional[HeadingContext] = Field(None, description="上下文信息")

    @field_validator('confidence')
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class HeadingInfo(BaseModel):
    """标题信息"""
    page: int = Field(..., description="页码", gt=0)
    line: int = Field(..., description="行号", gt=0)
    content: str = Field(..., description="标题内容")
    heading_id: str = Field(description="标题唯一标识符 (从1开始的自然数序号的字符串形式，如 '1', '2', '3')")
    current_level: Optional[int] = Field(None, description="当前层级", ge=1, le=6)
    expected_level: int = Field(..., description="期望层级", ge=1, le=6)
    confidence: float = Field(..., description="置信度", ge=0.8, le=1.0)
    validation: Optional[HeadingValidation] = Field(None, description="验证结果")
    related_headings: List[str] = Field(default_factory=list, description="相关标题ID列表")

    @field_validator('heading_id')
    def validate_heading_id(cls, v):
        """验证heading_id是否为有效的自然数字符串"""
        try:
            num = int(v)
            if num < 1:
                raise ValueError('Heading ID must be a positive integer')
        except ValueError:
            raise ValueError('Heading ID must be a string representation of a positive integer (e.g., "1", "2", "3")')
        return v

class HeadingRemoveInfo(BaseModel):
    """需要移除的内容信息"""
    page: int = Field(..., gt=0, description="页码")
    lines: List[int] = Field(..., min_length=1, description="行号列表")
    reason: HeadingRemoveReason = Field(..., description="移除原因")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    pattern: HeadingHeaderPattern = Field(..., description="页眉页脚模式")

class HeadingStructureValidation(BaseModel):
    """文档结构验证"""
    is_valid: bool = Field(..., description="结构是否有效")
    missing_levels: List[int] = Field(default_factory=list, description="缺失的层级")
    level_gaps: List[_HeadingLevelGapInfo] = Field(default_factory=list, description="层级断层")
    cross_page_issues: List[_HeadingCrossPageInfo] = Field(default_factory=list, description="跨页问题")

class DocumentAnalysisHeading(BaseModel):
    """文档分析结果"""
    headings: List[HeadingInfo] = Field(default_factory=list, description="标题信息列表")
    remove_infos: List[HeadingRemoveInfo] = Field(default_factory=list, description="需要移除的内容")
    structure_validation: HeadingStructureValidation = Field(..., description="结构验证结果")
    warnings: List[_HeadingWarningInfo] = Field(default_factory=list, description="警告信息")
    total_pages: int = Field(..., gt=0, description="总页数")
    total_headings: int = Field(..., ge=0, description="标题总数")

if __name__ == "__main__":
    # Ensure project root directory is used
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test data
    test_docs = [
        # 测试用例1：基本的标题错误和页眉
        {
            "headings": [
                {
                    "page": 1,
                    "line": 5,
                    "content": "1.2 系统架构",
                    "heading_id": "1",
                    "current_level": 2,
                    "expected_level": 2,
                    "confidence": 0.95,
                    "validation": {
                        "is_valid": True,
                        "current_level": 2,
                        "expected_level": 2,
                        "error_type": None,
                        "validation_scope": "single_page",
                        "confidence": 0.95,
                        "judgment_basis": {
                            "format_features": ["number_format"],
                            "content_features": ["length"],
                            "context_features": ["section_level"],
                            "position_features": ["para_start"]
                        },
                        "context": {
                            "prev_heading_id": "1",
                            "prev_level": 1,
                            "is_cross_page": False
                        }
                    }
                }
            ],
            "remove_infos": [
                {
                    "page": 1,
                    "lines": [1, 2],
                    "reason": "header",
                    "confidence": 0.98,
                    "pattern": "title_page"
                }
            ],
            "structure_validation": {
                "is_valid": True,
                "missing_levels": [],
                "level_gaps": [
                    {
                        "type": "skip_level",
                        "start_level": 1,
                        "end_level": 3,
                        "page": 1
                    }
                ],
                "cross_page_issues": [
                    {
                        "type": "break_heading",
                        "start_page": 1,
                        "end_page": 2,
                        "heading_index": 0
                    }
                ]
            },
            "warnings": [
                {
                    "type": "structure",
                    "page": 1,
                    "lines": [5],
                    "message": "标题层级跳跃"
                }
            ],
            "total_pages": 3,
            "total_headings": 1
        },
        
        # 测试用例2：错误类型和页脚
        {
            "headings": [
                {
                    "page": 1,
                    "line": 10,
                    "content": "普通段落",
                    "heading_id": "3",
                    "current_level": 2,
                    "expected_level": 1,
                    "confidence": 0.92,
                    "validation": {
                        "is_valid": False,
                        "current_level": 2,
                        "expected_level": 1,
                        "error_type": "not_heading",
                        "validation_scope": "single_page",
                        "confidence": 0.92,
                        "judgment_basis": {
                            "format_features": ["font_style"],
                            "content_features": ["length"],
                            "context_features": ["content_flow"],
                            "position_features": ["para_start"]
                        },
                        "context": {
                            "prev_heading": "1. 引言",
                            "prev_level": 1,
                            "is_cross_page": False
                        }
                    }
                }
            ],
            "remove_infos": [
                {
                    "page": 1,
                    "lines": [20],
                    "reason": "footer",
                    "confidence": 0.96,
                    "pattern": "number_only"
                }
            ],
            "structure_validation": {
                "is_valid": False,
                "missing_levels": [2],
                "level_gaps": [],
                "cross_page_issues": []
            },
            "warnings": [
                {
                    "type": "format",
                    "page": 1,
                    "lines": [10],
                    "message": "错误识别为标题"
                }
            ],
            "total_pages": 2,
            "total_headings": 1
        },
        
        # 测试用例3：复杂的页眉页脚模式和跨页问题
        {
            "headings": [
                {
                    "page": 2,
                    "line": 1,
                    "content": "2.1.1 详细设计",
                    "heading_id": "2",
                    "current_level": 3,
                    "expected_level": 3,
                    "confidence": 0.98,
                    "validation": {
                        "is_valid": True,
                        "current_level": 3,
                        "expected_level": 3,
                        "error_type": None,
                        "validation_scope": "cross_page",
                        "confidence": 0.98,
                        "judgment_basis": {
                            "format_features": ["number_format", "indent"],
                            "content_features": ["keywords"],
                            "context_features": ["section_level", "sequence"],
                            "position_features": ["page_top"]
                        },
                        "context": {
                            "prev_heading": "2.1 系统设计",
                            "prev_level": 2,
                            "is_cross_page": True
                        }
                    }
                }
            ],
            "remove_infos": [
                {
                    "page": 2,
                    "lines": [1, 2],
                    "reason": "header",
                    "confidence": 0.99,
                    "pattern": "chapter_title"
                },
                {
                    "page": 2,
                    "lines": [25],
                    "reason": "separator",
                    "confidence": 0.99,
                    "pattern": "custom"
                }
            ],
            "structure_validation": {
                "is_valid": True,
                "missing_levels": [],
                "level_gaps": [],
                "cross_page_issues": [
                    {
                        "type": "lost_context",
                        "start_page": 1,
                        "end_page": 2,
                        "heading_index": 0
                    }
                ]
            },
            "warnings": [
                {
                    "type": "cross_page",
                    "page": 2,
                    "lines": [1],
                    "message": "上下文跨页"
                }
            ],
            "total_pages": 2,
            "total_headings": 1
        }
    ]
    
    # Validate documents
    for i, test_doc in enumerate(test_docs, 1):
        print(f"\n测试用例 {i}:")
        try:
            result = DocumentAnalysisHeading.model_validate(test_doc)
            print(f"验证成功: {result.headings[0].content}")
        except Exception as e:
            print(f"验证失败: {str(e)}") 