import pytest
from unittest.mock import patch
from mrag_app._rag_core_query import do_core_query
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer
from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection

@pytest.mark.integration
@patch('mrag_app._rag_core_query.query2section_raw_on_rag_context')
@patch('mrag_app._rag_core_query.query2sortedsections_reranked')
@patch('mrag_app._rag_core_query.gen_answer_from_knowledge_snippets')
@patch('mrag_app._rag_core_query.compose_rag_answer')
def test_do_core_query_basic(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试RAG核心查询的基本功能"""
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
    response = do_core_query("椅背板与旁侧板的保留运动间隙是多少？", kb_name="mrag")
    
    assert isinstance(response, RagResponse)
    assert response.status == "success"
    assert response.user_input == "椅背板与旁侧板的保留运动间隙是多少？"
    assert len(response.progress_steps) > 0
    assert response.rag_answer == mock_answer
    assert isinstance(response.rag_answer.answer, str)
    assert len(response.rag_answer.answer) > 0

@pytest.mark.integration
@patch('mrag_app._rag_core_query.query2section_raw_on_rag_context')
@patch('mrag_app._rag_core_query.query2sortedsections_reranked')
@patch('mrag_app._rag_core_query.gen_answer_from_knowledge_snippets')
@patch('mrag_app._rag_core_query.compose_rag_answer')
def test_do_core_query_error_handling(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试RAG核心查询的错误处理"""
    # 设置mock返回值为None来模拟错误
    mock_raw.return_value = None
    
    response = do_core_query("测试问题", kb_name="invalid_kb")
    
    assert isinstance(response, RagResponse)
    assert response.status == "failed"
    assert response.error_message is not None
    assert response.rag_answer.answer == ""

@patch('mrag_app._rag_core_query.query2section_raw_on_rag_context')
def test_do_core_query_knowledge_retrieval_failure(mock_query2section):
    """测试RAG知识检索失败的情况"""
    mock_query2section.return_value = None
    
    response = do_core_query("测试问题", kb_name="mrag")
    
    assert response.status == "failed"
    assert "retrieval knowledge is None" in response.error_message

@patch('mrag_app._rag_core_query.query2section_raw_on_rag_context')
@patch('mrag_app._rag_core_query.query2sortedsections_reranked')
@patch('mrag_app._rag_core_query.gen_answer_from_knowledge_snippets')
@patch('mrag_app._rag_core_query.compose_rag_answer')
def test_do_core_query_answer_generation_failure(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试RAG答案生成失败的情况"""
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

@patch('mrag_app._rag_core_query.query2section_raw_on_rag_context')
@patch('mrag_app._rag_core_query.query2sortedsections_reranked')
@patch('mrag_app._rag_core_query.gen_answer_from_knowledge_snippets')
@patch('mrag_app._rag_core_query.compose_rag_answer')
def test_do_core_query_progress_steps(mock_compose, mock_gen_answer, mock_rerank, mock_raw):
    """测试RAG核心查询的进度步骤"""
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
    """测试RAG请求ID的生成"""
    # 设置两个不同的req_id
    mock_randint.side_effect = [12345, 67890]
    
    with patch('mrag_app._rag_core_query.query2section_raw_on_rag_context') as mock_raw:
        mock_raw.return_value = ["mock_section"]  # 避免实际API调用
        
        response1 = do_core_query("测试问题1", kb_name="mrag")
        response2 = do_core_query("测试问题2", kb_name="mrag")
    
        assert response1.req_id == 12345
        assert response2.req_id == 67890
        assert response1.req_id != response2.req_id 