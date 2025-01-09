import pytest

from mrag_app._app_qa_core import _QueryState, main_loop_gradio
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """每个测试前后自动清理状态"""
    _QueryState.reset()
    yield
    _QueryState.reset()

@pytest.fixture
def sample_response():
    """创建一个示例RAG响应"""
    return RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    )

@pytest.mark.unit
def test_query_state_lifecycle(sample_response):
    """测试应用层查询状态的生命周期管理"""
    # 初始状态应该是 None
    assert _QueryState.get_response() is None
    
    # 设置响应
    _QueryState.set_response(sample_response)
    
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
    """测试应用层查询状态的多次更新"""
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
    """测试应用层查询状态重置的行为"""
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

@pytest.fixture
def mock_core_query(monkeypatch, sample_response):
    """模拟核心查询函数"""
    def _mock_query(user_input, kb_name=None, limit=None):
        return sample_response
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", _mock_query)

@pytest.mark.integration
def test_main_loop_gradio_basic(mock_core_query, sample_response):
    """测试Gradio主循环的基本功能"""
    # 执行测试
    main_loop_gradio("测试问题", kb_name="test_kb")
    
    # 验证状态
    current_response = _QueryState.get_response()
    assert current_response is not None
    assert current_response.status == "success"
    assert current_response.rag_answer.answer == "测试回答"
    assert len(current_response.progress_steps) > 0

@pytest.fixture
def mock_core_query_error(monkeypatch):
    """模拟核心查询函数抛出错误"""
    def _mock_query(*args, **kwargs):
        raise Exception("测试错误")
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", _mock_query)

@pytest.mark.integration
def test_main_loop_gradio_error_handling(mock_core_query_error):
    """测试Gradio主循环的错误处理"""
    # 执行测试
    main_loop_gradio("测试问题")
    
    # 验证错误响应
    error_response = _QueryState.get_response()
    assert error_response is not None
    assert error_response.status == "failed"
    assert "测试错误" in error_response.error_message
    assert error_response.rag_answer.answer == ""
    
    # 验证进度步骤
    progress_steps = error_response.progress_steps
    assert len(progress_steps) > 0
    error_step = next((step for step in progress_steps if step.step == "error"), None)
    assert error_step is not None
    assert "测试错误" in error_step.task_name

@pytest.mark.integration
def test_main_loop_gradio_progress_tracking(mock_core_query):
    """测试Gradio主循环的进度跟踪"""
    # 执行测试
    main_loop_gradio("测试问题")
    
    # 验证进度步骤
    current_response = _QueryState.get_response()
    progress_steps = current_response.progress_steps
    
    # 验证有进度步骤
    assert len(progress_steps) > 0
    
    # 验证最终状态
    assert current_response.status == "success"
    assert current_response.error_message is None
    
    # 验证最终进度
    final_step = progress_steps[-1]
    assert final_step.progress == 100  # 确保完成
    assert "查询退出" in final_step.task_name  # 最后一步是查询退出 