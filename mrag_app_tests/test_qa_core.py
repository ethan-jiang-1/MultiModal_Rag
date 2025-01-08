import pytest
from unittest.mock import patch
from mrag_app._qa_core import ProgressStep, RagResponse, do_core_query
from mrag_vdb.dto.rag_answer import RagAnswer 
from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection

def test_progress_step_creation():
    """测试ProgressStep的创建和属性"""
    # 基本创建测试
    step = ProgressStep(
        step="step1",
        progress=50,
        task_name="测试任务",
        extra_info="额外信息"
    )
    assert step.step == "step1"
    assert step.progress == 50
    assert step.task_name == "测试任务"
    assert step.extra_info == "额外信息"

    # 测试可选字段
    step_no_extra = ProgressStep(
        step="step2",
        progress=75,
        task_name="测试任务2"
    )
    assert step_no_extra.extra_info is None

def test_rag_response_creation():
    """测试RagResponse的基本创建"""
    # 测试成功响应
    rag_answer = RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    response = RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=rag_answer
    )
    
    assert response.status == "success"
    assert response.error_message is None
    assert response.req_id == 12345
    assert response.user_input == "测试问题"
    assert response.rag_answer == rag_answer
    assert isinstance(response.progress_steps, list)
    assert len(response.progress_steps) == 0

def test_rag_response_factory_methods():
    """测试RagResponse的工厂方法"""
    # 测试成功工厂方法
    rag_answer = RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    success_response = RagResponse.from_success(
        req_id=12345,
        user_input="测试问题",
        rag_answer=rag_answer
    )
    assert success_response.status == "success"
    assert success_response.error_message is None
    
    # 测试失败工厂方法
    error_response = RagResponse.from_error(
        req_id=12345,
        user_input="测试问题",
        error_msg="测试错误"
    )
    assert error_response.status == "failed"
    assert error_response.error_message == "测试错误"
    assert error_response.rag_answer.answer == ""

def test_rag_response_progress_tracking():
    """测试RagResponse的进度跟踪功能"""
    response = RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=RagAnswer(answer="", answer_referenced="")
    )
    
    # 添加进度
    response.add_progress("step1", 25, "任务1", "额外信息1")
    response.add_progress("step2", 50, "任务2")
    response.add_progress("step3", 75, "任务3", "额外信息3")
    
    assert len(response.progress_steps) == 3
    assert response.progress_steps[0].progress == 25
    assert response.progress_steps[1].extra_info is None
    assert response.progress_steps[2].task_name == "任务3"

@pytest.mark.integration
@patch('mrag_app._qa_core.query2section_raw_on_rag_context')
@patch('mrag_app._qa_core.query2sortedsections_reranked')
@patch('mrag_app._qa_core.gen_answer_from_knowledge_snippets')
@patch('mrag_app._qa_core.compose_rag_answer')
def test_do_core_query_basic(mock_compose, mock_gen_answer, mock_rerank, mock_raw, mock_kb_name):
    """测试do_core_query的基本功能"""
    # 设置mock返回值
    mock_section = ScoredRecoveredSection(
        score=0.8,
        score_rrf=0.9,
        sec_id="1.1",
        parent_sec_id="1",
        heading="测试章节",
        level=1,
        desc="测试描述",
        doc_unique_id="test_doc",
        doc_title="测试文档",
        doc_ctn_type="text",
        fname_org_doc="test.md",
        content="测试内容",
        sec_seq_no=0,
        payloads=[],
        knowledge_snippet=None,
        collection_name="test_collection"
    )
    mock_raw.return_value = [mock_section]
    mock_rerank.return_value = [mock_section]
    mock_gen_answer.return_value = {"answer": "测试回答", "answer_referenced": "带引用的回答"}
    mock_answer = RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    mock_compose.return_value = mock_answer
    
    # 使用一个简单的查询
    response = do_core_query("椅背板与旁侧板的保留运动间隙是多少？", kb_name=mock_kb_name)
    
    assert isinstance(response, RagResponse)
    assert response.status == "success"
    assert response.user_input == "椅背板与旁侧板的保留运动间隙是多少？"
    assert len(response.progress_steps) > 0
    assert response.rag_answer == mock_answer
    assert isinstance(response.rag_answer.answer, str)
    assert len(response.rag_answer.answer) > 0

@pytest.mark.integration
@patch('mrag_app._qa_core.query2section_raw_on_rag_context')
@patch('mrag_app._qa_core.query2sortedsections_reranked')
@patch('mrag_app._qa_core.gen_answer_from_knowledge_snippets')
@patch('mrag_app._qa_core.compose_rag_answer')
def test_do_core_query_error_handling(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试do_core_query的错误处理"""
    # 设置mock返回值为None来模拟错误
    mock_raw.return_value = None
    
    response = do_core_query("测试问题", kb_name="invalid_kb")
    
    assert isinstance(response, RagResponse)
    assert response.status == "failed"
    assert response.error_message is not None
    assert response.rag_answer.answer == ""

@patch('mrag_app._qa_core.query2section_raw_on_rag_context')
def test_do_core_query_knowledge_retrieval_failure(mock_query2section):
    """测试知识检索失败的情况"""
    mock_query2section.return_value = None
    
    response = do_core_query("测试问题", kb_name="mrag")
    
    assert response.status == "failed"
    assert "retrieval knowledge is None" in response.error_message

@patch('mrag_app._qa_core.query2section_raw_on_rag_context')
@patch('mrag_app._qa_core.query2sortedsections_reranked')
@patch('mrag_app._qa_core.gen_answer_from_knowledge_snippets')
@patch('mrag_app._qa_core.compose_rag_answer')
def test_do_core_query_answer_generation_failure(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试答案生成失败的情况"""
    # 设置mock返回值
    mock_section = ScoredRecoveredSection(
        score=0.8,
        score_rrf=0.9,
        sec_id="1.1",
        parent_sec_id="1",
        heading="测试章节",
        level=1,
        desc="测试描述",
        doc_unique_id="test_doc",
        doc_title="测试文档",
        doc_ctn_type="text",
        fname_org_doc="test.md",
        content="测试内容",
        sec_seq_no=0,
        payloads=[],
        knowledge_snippet=None,
        collection_name="test_collection"
    )
    mock_raw.return_value = [mock_section]
    mock_rerank.return_value = [mock_section]
    mock_gen_answer.return_value = None
    
    response = do_core_query("测试问题", kb_name="mrag")
    
    assert response.status == "failed"
    assert "llm response is None" in response.error_message

@patch('mrag_app._qa_core.query2section_raw_on_rag_context')
@patch('mrag_app._qa_core.query2sortedsections_reranked')
@patch('mrag_app._qa_core.gen_answer_from_knowledge_snippets')
@patch('mrag_app._qa_core.compose_rag_answer')
def test_do_core_query_progress_steps(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试do_core_query的进度步骤"""
    # 设置mock返回值
    mock_section = ScoredRecoveredSection(
        score=0.8,
        score_rrf=0.9,
        sec_id="1.1",
        parent_sec_id="1",
        heading="测试章节",
        level=1,
        desc="测试描述",
        doc_unique_id="test_doc",
        doc_title="测试文档",
        doc_ctn_type="text",
        fname_org_doc="test.md",
        content="测试内容",
        sec_seq_no=0,
        payloads=[],
        knowledge_snippet=None,
        collection_name="test_collection"
    )
    mock_raw.return_value = [mock_section]
    mock_rerank.return_value = [mock_section]
    mock_gen_answer.return_value = {"answer": "测试回答", "answer_referenced": "带引用的回答"}
    mock_answer = RagAnswer(answer="测试回答", answer_referenced="带引用的回答")
    mock_compose.return_value = mock_answer
    
    response = do_core_query("测试问题", kb_name="mrag")
    
    # 验证进度步骤
    progress_steps = [(step.step, step.progress) for step in response.progress_steps]
    expected_steps = [
        ("step1", 10),  # 选择知识库
        ("step2", 20),  # 准备查询
        ("step3", 30),  # 召回知识(raw)
        ("step4", 40),  # 召回知识(rerank)
        ("step5", 50),  # 组织知识
        ("step6", 60),  # 生成回答(文本)
        ("step7", 80),  # 生成回答(图像)
        ("step8", 95),  # 完成回答
    ]
    
    for expected, actual in zip(expected_steps, progress_steps):
        assert expected[0] == actual[0], f"步骤名称不匹配: {expected[0]} != {actual[0]}"
        assert expected[1] == actual[1], f"进度值不匹配: {expected[1]} != {actual[1]}"

@patch('random.randint')
def test_do_core_query_req_id_generation(mock_randint):
    """测试请求ID的生成"""
    # 设置两个不同的req_id
    mock_randint.side_effect = [12345, 67890]
    
    with patch('mrag_app._qa_core.query2section_raw_on_rag_context') as mock_raw:
        mock_raw.return_value = ["mock_section"]  # 避免实际API调用
        
        response1 = do_core_query("测试问题1", kb_name="mrag")
        response2 = do_core_query("测试问题2", kb_name="mrag")
    
        assert response1.req_id == 12345
        assert response2.req_id == 67890
        assert response1.req_id != response2.req_id 