import pytest
from mrag_app._app_qa_core import RagResponse, _QueryState
from mrag_vdb.dto.rag_answer import RagAnswer

@pytest.mark.unit
def test_query_state_lifecycle():
    """测试查询状态的生命周期管理"""
    # 初始状态应该是 None
    assert _QueryState.get_response() is None
    
    # 设置响应
    test_response = RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    )
    _QueryState.set_response(test_response)
    
    # 验证能够获取到设置的响应
    current_response = _QueryState.get_response()
    assert current_response is not None
    assert current_response.req_id == 12345
    assert current_response.user_input == "测试问题"
    assert current_response.rag_answer.answer == "测试回答"
    
    # 重置状态
    _QueryState.reset()
    assert _QueryState.get_response() is None

@pytest.mark.unit
def test_query_state_multiple_updates():
    """测试查询状态的多次更新"""
    # 第一次更新
    response1 = RagResponse(
        req_id=1,
        user_input="问题1",
        rag_answer=RagAnswer(answer="回答1", answer_referenced="引用1")
    )
    _QueryState.set_response(response1)
    assert _QueryState.get_response().req_id == 1
    
    # 第二次更新
    response2 = RagResponse(
        req_id=2,
        user_input="问题2",
        rag_answer=RagAnswer(answer="回答2", answer_referenced="引用2")
    )
    _QueryState.set_response(response2)
    assert _QueryState.get_response().req_id == 2
    
    # 确保是最新的状态
    current = _QueryState.get_response()
    assert current.user_input == "问题2"
    assert current.rag_answer.answer == "回答2"

@pytest.mark.unit
def test_query_state_reset_behavior():
    """测试查询状态重置的行为"""
    # 设置初始状态
    initial_response = RagResponse(
        req_id=123,
        user_input="测试问题",
        rag_answer=RagAnswer(answer="测试回答", answer_referenced="引用")
    )
    _QueryState.set_response(initial_response)
    
    # 验证状态已设置
    assert _QueryState.get_response() is not None
    
    # 重置状态
    _QueryState.reset()
    
    # 验证重置后的状态
    assert _QueryState.get_response() is None
    
    # 再次设置新状态，确保可以正常工作
    new_response = RagResponse(
        req_id=456,
        user_input="新问题",
        rag_answer=RagAnswer(answer="新回答", answer_referenced="新引用")
    )
    _QueryState.set_response(new_response)
    assert _QueryState.get_response().req_id == 456 