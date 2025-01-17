"""Test cases for heading data schemas"""

import pytest
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    HeadingJudgmentBasis,
    HeadingContext,
    HeadingValidation,
    HeadingInfo,
    HeadingRemoveInfo,
    HeadingStructureValidation,
    DocumentAnalysisHeading,
)

# 基础测试数据
@pytest.fixture
def valid_judgment_basis():
    return {
        "format_features": ["number_format", "indent"],
        "content_features": ["length", "topic"],
        "context_features": ["section_level"],
        "position_features": ["para_start"]
    }

@pytest.fixture
def valid_context():
    return {
        "prev_heading": "1. 引言",
        "prev_level": 1,
        "is_cross_page": False
    }

@pytest.fixture
def valid_validation():
    return {
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
            "prev_heading": "1. 引言",
            "prev_level": 1,
            "is_cross_page": False
        }
    }

@pytest.fixture
def valid_heading():
    return {
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
                "prev_heading": "1. 引言",
                "prev_level": 1,
                "is_cross_page": False
            }
        }
    }

@pytest.fixture
def valid_document():
    return {
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
                "lines": [1, 2],
                "reason": "header",
                "confidence": 0.98,
                "pattern": "title_page"
            }
        ],
        "structure_validation": {
            "is_valid": True,
            "missing_levels": [],
            "level_gaps": [],
            "cross_page_issues": []
        },
        "warnings": [],
        "total_pages": 3,
        "total_headings": 1
    }

# 测试基础组件
def test_heading_judgment_basis(valid_judgment_basis):
    """测试判断依据的创建和验证"""
    basis = HeadingJudgmentBasis(**valid_judgment_basis)
    assert basis.format_features == ["number_format", "indent"]
    assert basis.content_features == ["length", "topic"]
    assert basis.context_features == ["section_level"]
    assert basis.position_features == ["para_start"]

def test_heading_context(valid_context):
    """测试标题上下文的创建和验证"""
    context = HeadingContext(**valid_context)
    assert context.prev_heading == "1. 引言"
    assert context.prev_level == 1
    assert not context.is_cross_page

def test_heading_validation(valid_validation):
    """测试标题验证的创建和验证"""
    validation = HeadingValidation(**valid_validation)
    assert validation.is_valid
    assert validation.current_level == 2
    assert validation.confidence == 0.95

def test_heading_info(valid_heading):
    """测试标题信息的创建和验证"""
    heading = HeadingInfo(**valid_heading)
    assert heading.content == "1.2 系统架构"
    assert heading.confidence == 0.95
    assert heading.validation.is_valid

def test_document_analysis(valid_document):
    """测试文档分析结果的创建和验证"""
    doc = DocumentAnalysisHeading(**valid_document)
    assert len(doc.headings) == 1
    assert doc.total_pages == 3
    assert doc.total_headings == 1

# 测试错误情况
def test_invalid_confidence():
    """测试无效的置信度"""
    with pytest.raises(ValueError):
        HeadingValidation(
            is_valid=True,
            validation_scope="single_page",
            confidence=1.5  # 超出范围
        )

def test_invalid_level():
    """测试无效的标题层级"""
    with pytest.raises(ValueError):
        HeadingInfo(
            page=1,
            line=5,
            content="标题",
            current_level=7,  # 超出范围
            confidence=0.9,
            validation=HeadingValidation(
                is_valid=True,
                validation_scope="single_page",
                confidence=0.9
            )
        )

def test_invalid_enum_value():
    """测试无效的枚举值"""
    with pytest.raises(ValueError):
        HeadingRemoveInfo(
            page=1,
            lines=[1],
            reason="invalid_reason",  # 无效的枚举值
            confidence=0.9,
            pattern="title_page"
        )

# 测试边界情况
def test_empty_features():
    """测试空特征列表"""
    basis = HeadingJudgmentBasis()
    assert len(basis.format_features) == 0
    assert len(basis.content_features) == 0

def test_minimal_document():
    """测试最小文档"""
    doc = DocumentAnalysisHeading(
        headings=[],
        structure_validation={"is_valid": True},
        total_pages=1,
        total_headings=0
    )
    assert doc.total_headings == 0
    assert len(doc.headings) == 0

def test_cross_page_context():
    """测试跨页上下文"""
    context = HeadingContext(
        prev_heading="上一页标题",
        prev_level=1,
        is_cross_page=True
    )
    assert context.is_cross_page

# 测试复杂场景
def test_multiple_warnings():
    """测试多个警告"""
    doc = DocumentAnalysisHeading(
        headings=[],
        structure_validation={"is_valid": True},
        warnings=[
            {
                "type": "structure",
                "page": 1,
                "lines": [5],
                "message": "警告1"
            },
            {
                "type": "format",
                "page": 2,
                "lines": [10],
                "message": "警告2"
            }
        ],
        total_pages=2,
        total_headings=0
    )
    assert len(doc.warnings) == 2

def test_complex_structure_validation():
    """测试复杂的结构验证"""
    validation = HeadingStructureValidation(
        is_valid=False,
        missing_levels=[2, 4],
        level_gaps=[
            {
                "type": "skip_level",
                "start_level": 1,
                "end_level": 3,
                "page": 1
            }
        ],
        cross_page_issues=[
            {
                "type": "lost_context",
                "start_page": 1,
                "end_page": 2,
                "heading_index": 0
            }
        ]
    )
    assert not validation.is_valid
    assert len(validation.missing_levels) == 2
    assert len(validation.level_gaps) == 1
    assert len(validation.cross_page_issues) == 1 