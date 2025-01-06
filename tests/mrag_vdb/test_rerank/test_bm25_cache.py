import pytest
from mrag_vdb.rerank._bm25_cache import TokenizedDocBM25
import msgpack

@pytest.fixture
def sample_tokenized_doc():
    return ["机器", "学习", "是", "人工智能", "的", "一个", "分支"]

@pytest.fixture
def sample_queries():
    return [
        "机器学习",
        "深度学习",
        "人工智能"
    ]

def test_tokenized_doc_bm25_basic(sample_tokenized_doc, sample_queries):
    """测试TokenizedDocBM25的基本功能"""
    # 创建实例
    bm25 = TokenizedDocBM25(sample_tokenized_doc)
    
    # 测试get_tokenized_doc
    assert bm25.get_tokenized_doc() == sample_tokenized_doc
    
    # 测试单个查询
    score = bm25.get_score("机器学习")
    assert isinstance(score, float)
    assert score > 0  # 相关查询应该有正分数

    # 测试多个查询
    scores = bm25.get_scores(sample_queries)
    assert len(scores) == len(sample_queries)
    assert all(isinstance(s, float) for s in scores)

def test_tokenized_doc_bm25_serialization(sample_tokenized_doc):
    """测试序列化和反序列化功能"""
    original_bm25 = TokenizedDocBM25(sample_tokenized_doc)
    
    # 序列化
    cache_data = original_bm25.to_cache()
    assert "tokenized_doc" in cache_data
    assert "version" in cache_data
    assert cache_data["tokenized_doc"] == sample_tokenized_doc
    
    # 使用msgpack序列化和反序列化
    packed = msgpack.packb(cache_data)
    unpacked = msgpack.unpackb(packed)
    
    # 从缓存恢复
    restored_bm25 = TokenizedDocBM25.from_cache(unpacked)
    
    # 验证恢复后的结果
    test_query = "机器学习"
    original_score = original_bm25.get_score(test_query)
    restored_score = restored_bm25.get_score(test_query)
    assert abs(original_score - restored_score) < 1e-6

def test_tokenized_doc_bm25_error_handling():
    """测试错误处理"""
    # 测试空文档
    with pytest.raises(ValueError):
        TokenizedDocBM25.from_cache({})
    
    # 测试缺少tokenized_doc字段
    with pytest.raises(ValueError):
        TokenizedDocBM25.from_cache({"version": "1.0"}) 