"""Test cases for complex heading structure scenarios"""

import pytest
from dotenv import load_dotenv
load_dotenv()

from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
)

@pytest.fixture
def complex_document_with_gaps():
    """具有层级跳跃的复杂文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 5,
                "content": "1. 引言",
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 1,
                    "expected_level": 1,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            },
            {
                "page": 1,
                "line": 15,
                "content": "1.3 系统概述",  # 缺少 1.1 和 1.2
                "current_level": 2,
                "expected_level": 2,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 2,
                    "expected_level": 2,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            }
        ],
        "structure_validation": {
            "is_valid": False,
            "missing_levels": [2],  # 缺少二级标题
            "level_gaps": [
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 2,
                    "page": 1
                }
            ],
            "cross_page_issues": []
        },
        "warnings": [
            {
                "type": "structure",
                "page": 1,
                "lines": [15],
                "message": "缺少 1.1 和 1.2 节"
            }
        ],
        "total_pages": 2,
        "total_headings": 2
    }

@pytest.fixture
def complex_document_with_wrong_order():
    """标题顺序错误的复杂文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 5,
                "content": "2. 详细设计",  # 错误的顺序
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 1,
                    "expected_level": 1,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            },
            {
                "page": 1,
                "line": 15,
                "content": "1. 引言",  # 应该在前面
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 1,
                    "expected_level": 1,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            }
        ],
        "structure_validation": {
            "is_valid": False,
            "missing_levels": [],
            "level_gaps": [
                {
                    "type": "wrong_order",
                    "start_level": 1,
                    "end_level": 1,
                    "page": 1
                }
            ],
            "cross_page_issues": []
        },
        "warnings": [
            {
                "type": "structure",
                "page": 1,
                "lines": [5, 15],
                "message": "标题顺序错误"
            }
        ],
        "total_pages": 1,
        "total_headings": 2
    }

@pytest.fixture
def complex_document_with_wrong_level():
    """标题层级错误的复杂文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 5,
                "content": "1. 引言",
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 1,
                    "expected_level": 1,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            },
            {
                "page": 1,
                "line": 15,
                "content": "3.1.1 详细信息",  # 错误的层级
                "current_level": 3,
                "expected_level": 2,
                "confidence": 0.95,
                "validation": {
                    "is_valid": False,
                    "current_level": 3,
                    "expected_level": 2,
                    "error_type": "wrong_level",
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            }
        ],
        "structure_validation": {
            "is_valid": False,
            "missing_levels": [],
            "level_gaps": [
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 3,
                    "page": 1
                }
            ],
            "cross_page_issues": []
        },
        "warnings": [
            {
                "type": "structure",
                "page": 1,
                "lines": [15],
                "message": "标题层级错误"
            }
        ],
        "total_pages": 1,
        "total_headings": 2
    }

def test_document_with_gaps(complex_document_with_gaps):
    """测试具有层级跳跃的文档"""
    doc = DocumentAnalysisHeading(**complex_document_with_gaps)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.missing_levels) == 1
    assert len(doc.structure_validation.level_gaps) == 1
    assert doc.structure_validation.level_gaps[0].type == "skip_level"
    assert len(doc.warnings) == 1
    assert doc.warnings[0].type == "structure"

def test_document_with_wrong_order(complex_document_with_wrong_order):
    """测试标题顺序错误的文档"""
    doc = DocumentAnalysisHeading(**complex_document_with_wrong_order)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.level_gaps) == 1
    assert doc.structure_validation.level_gaps[0].type == "wrong_order"
    assert len(doc.warnings) == 1
    assert "顺序错误" in doc.warnings[0].message

def test_document_with_wrong_level(complex_document_with_wrong_level):
    """测试标题层级错误的文档"""
    doc = DocumentAnalysisHeading(**complex_document_with_wrong_level)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.level_gaps) == 1
    assert doc.structure_validation.level_gaps[0].type == "skip_level"
    assert doc.headings[1].validation.error_type == "wrong_level"
    assert len(doc.warnings) == 1
    assert "层级错误" in doc.warnings[0].message

def test_mixed_structure_issues():
    """测试混合的结构问题"""
    doc = DocumentAnalysisHeading(
        headings=[
            {
                "page": 1,
                "line": 5,
                "content": "2. 详细设计",
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 1,
                    "expected_level": 1,
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            },
            {
                "page": 1,
                "line": 15,
                "content": "2.1.1.1 具体实现",
                "current_level": 4,
                "expected_level": 2,
                "confidence": 0.95,
                "validation": {
                    "is_valid": False,
                    "current_level": 4,
                    "expected_level": 2,
                    "error_type": "wrong_level",
                    "validation_scope": "single_page",
                    "confidence": 0.95
                }
            }
        ],
        structure_validation={
            "is_valid": False,
            "missing_levels": [2, 3],
            "level_gaps": [
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 4,
                    "page": 1
                },
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 4,
                    "page": 1
                }
            ],
            "cross_page_issues": []
        },
        warnings=[
            {
                "type": "structure",
                "page": 1,
                "lines": [15],
                "message": "标题层级跳跃过大"
            }
        ],
        total_pages=1,
        total_headings=2
    )
    
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.missing_levels) == 2
    assert len(doc.structure_validation.level_gaps) == 2
    assert doc.headings[1].validation.error_type == "wrong_level"
    assert len(doc.warnings) == 1 