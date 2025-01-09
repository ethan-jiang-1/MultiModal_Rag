import pytest
from mrag_app._app_qa_core import _QueryState, main_loop_gradio
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer
from mrag_vdb.dto.rag_runtime_settings import RagKbNameSel, RagModelGptSel

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """每个测试前后自动清理状态"""
    _QueryState.reset()
    yield
    _QueryState.reset()

@pytest.fixture
def mock_rag_answer():
    """创建一个模拟的RAG回答"""
    return RagAnswer(
        answer="这是测试回答内容",
        answer_referenced="这是带引用的回答内容",
        source_names=["doc1.md", "doc2.md"],
        source_titles=["文档1", "文档2"],
        source_pnames=["/path/to/doc1", "/path/to/doc2"],
        image_names=["img1.png"],
        image_titles=["图片1"],
        image_pnames=["/path/to/img1"]
    )

@pytest.fixture
def mock_rag_response(mock_rag_answer):
    """创建一个模拟的RAG响应"""
    response = RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=mock_rag_answer
    )
    # 添加典型的进度步骤
    response.add_progress("step1", 10, "选择知识库:mrag")
    response.add_progress("step2", 50, "处理中", "正在检索")
    response.add_progress("step3", 100, "完成回答")
    return response

@pytest.mark.integration
def test_main_flow_mrag_kb(mock_rag_response, monkeypatch):
    """测试MRAG知识库的主要查询流程"""
    def mock_core_query(user_input, kb_name=None, limit=None):
        assert kb_name == "mrag", "应该使用mrag知识库"
        assert limit == 10, "默认应该使用10条限制"
        return mock_rag_response
    
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", mock_core_query)
    RagKbNameSel.set_kbname("mrag")  # 设置知识库
    
    # 执行主流程
    main_loop_gradio("椅背板与旁侧板的保留运动间隙是多少？")
    
    # 验证响应
    response = _QueryState.get_response()
    assert response is not None
    assert response.status == "success"
    assert len(response.progress_steps) > 0
    assert response.rag_answer.answer == "这是测试回答内容"
    # 验证文档和图片信息
    assert len(response.rag_answer.source_names) == 2
    assert len(response.rag_answer.image_names) == 1

@pytest.mark.integration
def test_main_flow_papers_kb(mock_rag_response, monkeypatch):
    """测试Papers知识库的主要查询流程"""
    def mock_core_query(user_input, kb_name=None, limit=None):
        assert kb_name == "papers", "应该使用papers知识库"
        return mock_rag_response
    
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", mock_core_query)
    RagKbNameSel.set_kbname("papers")  # 设置知识库
    
    # 执行主流程
    main_loop_gradio("什么是神经网络？")
    
    # 验证响应
    response = _QueryState.get_response()
    assert response is not None
    assert response.status == "success"

@pytest.mark.integration
def test_main_flow_with_different_models(mock_rag_response, monkeypatch):
    """测试不同模型的查询流程"""
    mock_calls = []
    
    def mock_core_query(user_input, kb_name=None, limit=None):
        mock_calls.append({"input": user_input, "kb": kb_name})
        return mock_rag_response
    
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", mock_core_query)
    
    # 测试不同的模型设置
    models = ["gpt-4", "gpt-35-turbo", "qwen-turbo", "qwen-plus"]
    for model in models:
        RagModelGptSel.set_gpt_model(model)
        main_loop_gradio("测试问题")
        
        response = _QueryState.get_response()
        assert response is not None
        assert response.status == "success"
        _QueryState.reset()  # 重置状态准备下一次测试

@pytest.mark.integration
def test_error_handling_flow(monkeypatch):
    """测试错误处理流程"""
    def mock_core_query(*args, **kwargs):
        raise Exception("模拟的API调用错误")
    
    monkeypatch.setattr("mrag_app._app_qa_core._do_core_query", mock_core_query)
    
    # 执行查询
    main_loop_gradio("测试问题")
    
    # 验证错误响应
    response = _QueryState.get_response()
    assert response is not None
    assert response.status == "failed"
    assert "模拟的API调用错误" in response.error_message
    
    # 验证错误进度步骤
    error_step = next((step for step in response.progress_steps if step.step == "error"), None)
    assert error_step is not None
    assert "模拟的API调用错误" in error_step.task_name 