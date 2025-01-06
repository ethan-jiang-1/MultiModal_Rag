import pytest
from mrag_vdb.dto.rag_answer import RagAnswer

@pytest.fixture
def sample_rag_answer():
    """返回一个用于测试的RagAnswer实例"""
    return RagAnswer(
        answer="这是一个测试回答",
        answer_referenced="这是一个带引用的测试回答"
    )

@pytest.fixture
def mock_kb_name():
    """返回一个用于测试的知识库名称"""
    return "mrag" 