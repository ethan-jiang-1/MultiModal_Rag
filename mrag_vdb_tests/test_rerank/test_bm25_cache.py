import pytest
import jieba
from mrag_vdb.rerank._bm25_cache import TokenizedDocBM25

def test_tokenized_doc_bm25_basic():
    """测试基本的BM25功能"""
    # 准备测试数据
    doc = "机器学习是人工智能的一个重要分支"
    tokenized_doc = list(jieba.cut(doc))
    bm25 = TokenizedDocBM25(tokenized_doc)
    
    # 测试单个查询
    query = "机器学习"
    score = bm25.get_score(query)
    assert isinstance(score, float), "分数应该是浮点数"
    
    # 测试多个查询
    queries = ["机器学习", "人工智能", "自然语言"]  # 最后一个是不相关的查询
    scores = bm25.get_scores(queries)
    assert len(scores) == len(queries), "分数列表长度应该与查询列表相同"
    assert all(isinstance(s, float) for s in scores), "所有分数都应该是浮点数"
    
    # 测试相关性排序（相关查询的分数应该高于不相关查询）
    # 由于BM25算法的特性，我们只需要验证分数的相对大小
    # 将所有分数转换为排名
    score_ranks = {score: rank for rank, score in enumerate(sorted(scores, reverse=True))}
    assert score_ranks[scores[0]] < score_ranks[scores[2]], "相关查询'机器学习'的排名应该高于不相关查询'自然语言'"
    assert score_ranks[scores[1]] < score_ranks[scores[2]], "相关查询'人工智能'的排名应该高于不相关查询'自然语言'"

def test_tokenized_doc_bm25_serialization():
    """测试BM25对象的序列化和反序列化"""
    # 准备测试数据
    doc = "机器学习是人工智能的一个重要分支"
    tokenized_doc = list(jieba.cut(doc))
    bm25_original = TokenizedDocBM25(tokenized_doc)
    
    # 序列化
    cache_data = bm25_original.to_cache()
    assert isinstance(cache_data, dict), "缓存数据应该是字典类型"
    assert "tokenized_doc" in cache_data, "缓存数据应该包含分词结果"
    assert cache_data["tokenized_doc"] == tokenized_doc, "缓存的分词结果应该与原始数据相同"
    
    # 反序列化
    bm25_restored = TokenizedDocBM25.from_cache(cache_data)
    assert isinstance(bm25_restored, TokenizedDocBM25), "应该恢复为TokenizedDocBM25对象"
    
    # 验证功能一致性
    query = "机器学习"
    score_original = bm25_original.get_score(query)
    score_restored = bm25_restored.get_score(query)
    assert score_original == score_restored, "序列化前后的分数应该相同"

def test_tokenized_doc_bm25_error_handling():
    """测试错误处理"""
    with pytest.raises(Exception):
        TokenizedDocBM25([])  # 空文档应该抛出异常 