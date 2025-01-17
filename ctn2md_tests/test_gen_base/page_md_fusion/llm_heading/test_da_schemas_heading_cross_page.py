"""Test cases for complex cross-page heading scenarios"""

import pytest
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
)

@pytest.fixture
def document_with_broken_heading():
    """标题被页面分割的文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 58,  # 页面底部
                "content": "1.2 系统",  # 标题前半部分
                "current_level": 2,
                "expected_level": 2,
                "confidence": 0.85,  # 降低置信度
                "validation": {
                    "is_valid": False,
                    "current_level": 2,
                    "expected_level": 2,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.85,
                    "context": {
                        "prev_heading": "1.1 背景",
                        "prev_level": 2,
                        "is_cross_page": True
                    }
                }
            },
            {
                "page": 2,
                "line": 1,  # 页面顶部
                "content": "架构设计",  # 标题后半部分
                "current_level": None,  # 不确定层级
                "expected_level": 2,
                "confidence": 0.85,
                "validation": {
                    "is_valid": False,
                    "current_level": None,
                    "expected_level": 2,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.85,
                    "context": {
                        "prev_heading": "1.2 系统",
                        "prev_level": 2,
                        "is_cross_page": True
                    }
                }
            }
        ],
        "structure_validation": {
            "is_valid": False,
            "missing_levels": [],
            "level_gaps": [],
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
                "lines": [58],
                "message": "标题可能在页面间断开"
            },
            {
                "type": "structure",
                "page": 2,
                "lines": [1],
                "message": "可能是上页标题的延续"
            }
        ],
        "total_pages": 2,
        "total_headings": 2
    }

@pytest.fixture
def document_with_lost_context():
    """跨页丢失上下文的文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 50,
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
                "page": 2,
                "line": 15,
                "content": "系统功能",  # 缺少编号
                "current_level": None,
                "expected_level": 2,
                "confidence": 0.8,  # 提高置信度到最小值
                "validation": {
                    "is_valid": False,
                    "current_level": None,
                    "expected_level": 2,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.8,
                    "context": {
                        "prev_heading": "1. 引言",
                        "prev_level": 1,
                        "is_cross_page": True
                    }
                }
            },
            {
                "page": 2,
                "line": 30,
                "content": "1.2 系统架构",  # 暗示前面应该是 1.1
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
            "missing_levels": [2],  # 缺少 1.1
            "level_gaps": [
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 2,
                    "page": 2
                }
            ],
            "cross_page_issues": [
                {
                    "type": "lost_context",
                    "start_page": 1,
                    "end_page": 2,
                    "heading_index": 1
                }
            ]
        },
        "warnings": [
            {
                "type": "structure",
                "page": 2,
                "lines": [15],
                "message": "标题可能缺少编号"
            }
        ],
        "total_pages": 2,
        "total_headings": 3
    }

@pytest.fixture
def document_with_mixed_cross_page():
    """复杂的跨页混合问题文档"""
    return {
        "headings": [
            {
                "page": 1,
                "line": 55,
                "content": "2. 系统",  # 被分割的标题开始
                "current_level": 1,
                "expected_level": 1,
                "confidence": 0.85,
                "validation": {
                    "is_valid": False,
                    "current_level": 1,
                    "expected_level": 1,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.85,
                    "context": {
                        "prev_heading": "1. 引言",
                        "prev_level": 1,
                        "is_cross_page": True
                    }
                }
            },
            {
                "page": 2,
                "line": 1,
                "content": "设计概述",  # 被分割的标题结束
                "current_level": None,
                "expected_level": 1,
                "confidence": 0.85,
                "validation": {
                    "is_valid": False,
                    "current_level": None,
                    "expected_level": 1,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.85,
                    "context": {
                        "prev_heading": "2. 系统",
                        "prev_level": 1,
                        "is_cross_page": True
                    }
                }
            },
            {
                "page": 2,
                "line": 20,
                "content": "功能模块",  # 缺少编号的标题
                "current_level": None,
                "expected_level": 2,
                "confidence": 0.8,  # 提高置信度到最小值
                "validation": {
                    "is_valid": False,
                    "current_level": None,
                    "expected_level": 2,
                    "error_type": "needs_level",
                    "validation_scope": "cross_page",
                    "confidence": 0.8,
                    "context": {
                        "prev_heading": "2. 系统设计概述",
                        "prev_level": 1,
                        "is_cross_page": True
                    }
                }
            },
            {
                "page": 3,
                "line": 1,
                "content": "2.2 接口设计",  # 暗示前面应该是 2.1
                "current_level": 2,
                "expected_level": 2,
                "confidence": 0.95,
                "validation": {
                    "is_valid": True,
                    "current_level": 2,
                    "expected_level": 2,
                    "validation_scope": "cross_page",
                    "confidence": 0.95,
                    "context": {
                        "prev_heading": "功能模块",
                        "prev_level": None,
                        "is_cross_page": True
                    }
                }
            }
        ],
        "structure_validation": {
            "is_valid": False,
            "missing_levels": [2],  # 缺少 2.1
            "level_gaps": [
                {
                    "type": "skip_level",
                    "start_level": 1,
                    "end_level": 2,
                    "page": 2
                }
            ],
            "cross_page_issues": [
                {
                    "type": "break_heading",
                    "start_page": 1,
                    "end_page": 2,
                    "heading_index": 0
                },
                {
                    "type": "lost_context",
                    "start_page": 2,
                    "end_page": 2,
                    "heading_index": 2
                }
            ]
        },
        "warnings": [
            {
                "type": "structure",
                "page": 1,
                "lines": [55],
                "message": "标题可能在页面间断开"
            },
            {
                "type": "structure",
                "page": 2,
                "lines": [1],
                "message": "可能是上页标题的延续"
            },
            {
                "type": "structure",
                "page": 2,
                "lines": [20],
                "message": "标题可能缺少编号"
            }
        ],
        "total_pages": 3,
        "total_headings": 4
    }

def test_broken_heading(document_with_broken_heading):
    """测试标题被页面分割的情况"""
    doc = DocumentAnalysisHeading(**document_with_broken_heading)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.cross_page_issues) == 1
    assert doc.structure_validation.cross_page_issues[0].type == "break_heading"
    assert doc.headings[0].validation.error_type == "needs_level"
    assert doc.headings[1].validation.error_type == "needs_level"
    assert doc.headings[0].validation.context.is_cross_page
    assert doc.headings[1].validation.context.is_cross_page
    assert len(doc.warnings) == 2

def test_lost_context(document_with_lost_context):
    """测试跨页丢失上下文的情况"""
    doc = DocumentAnalysisHeading(**document_with_lost_context)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.cross_page_issues) == 1
    assert doc.structure_validation.cross_page_issues[0].type == "lost_context"
    assert doc.headings[1].validation.error_type == "needs_level"
    assert doc.headings[1].current_level is None
    assert doc.headings[1].validation.context.is_cross_page
    assert len(doc.warnings) == 1

def test_mixed_cross_page_issues(document_with_mixed_cross_page):
    """测试复杂的跨页混合问题"""
    doc = DocumentAnalysisHeading(**document_with_mixed_cross_page)
    assert not doc.structure_validation.is_valid
    assert len(doc.structure_validation.cross_page_issues) == 2
    # 检查第一个跨页问题：标题断开
    assert doc.structure_validation.cross_page_issues[0].type == "break_heading"
    assert doc.headings[0].validation.error_type == "needs_level"
    assert doc.headings[1].validation.error_type == "needs_level"
    # 检查第二个跨页问题：丢失上下文
    assert doc.structure_validation.cross_page_issues[1].type == "lost_context"
    assert doc.headings[2].validation.error_type == "needs_level"
    assert doc.headings[2].current_level is None
    # 检查警告信息
    assert len(doc.warnings) == 3
    # 检查结构验证
    assert len(doc.structure_validation.missing_levels) == 1
    assert len(doc.structure_validation.level_gaps) == 1
    assert doc.structure_validation.level_gaps[0].type == "skip_level" 