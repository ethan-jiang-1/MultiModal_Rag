import pytest
import jieba
from mrag_vdb.rerank._bm25_cache import TokenizedDoc, compute_bm25_scores

def test_tokenized_doc_basic():
    """测试TokenizedDoc的基本功能"""
    # 准备测试数据
    doc = "机器学习是人工智能的一个重要分支"
    tokenized_doc = list(jieba.cut(doc))
    doc_obj = TokenizedDoc(tokenized_doc)
    
    # 测试获取分词结果
    assert doc_obj.get_tokenized_doc() == tokenized_doc, "分词结果应该与输入一致"

def test_bm25_basic_ranking():
    """测试BM25基本排序功能"""
    # 创建一组简单的测试文档
    docs = [
        TokenizedDoc(["测试", "文档"]),              # 文档0：无关文档
        TokenizedDoc(["机器", "学习"]),              # 文档1：完全匹配
        TokenizedDoc(["机器", "学习", "入门"])       # 文档2：包含额外词
    ]
    
    # 测试查询
    query = ["机器", "学习"]
    scores = compute_bm25_scores(query, docs)
    
    # 打印分数以便调试
    for i, score in enumerate(scores):
        print(f"文档 {i} ('{' '.join(docs[i].get_tokenized_doc())}') 得分: {score}")
    
    # 验证基本排序
    assert scores[1] > scores[0], "完全匹配文档的分数应该高于无关文档"
    assert scores[2] > scores[0], "部分匹配文档的分数应该高于无关文档"

def test_tokenized_doc_serialization():
    """测试TokenizedDoc的序列化和反序列化"""
    # 准备测试数据
    doc = "机器学习是人工智能的一个重要分支"
    tokenized_doc = list(jieba.cut(doc))
    doc_obj = TokenizedDoc(tokenized_doc)
    
    # 序列化
    cache_data = doc_obj.to_cache()
    assert isinstance(cache_data, dict), "缓存数据应该是字典类型"
    assert "tokenized_doc" in cache_data, "缓存数据应该包含分词结果"
    assert cache_data["tokenized_doc"] == tokenized_doc, "缓存的分词结果应该与原始数据相同"
    
    # 反序列化
    restored_doc = TokenizedDoc.from_cache(cache_data)
    assert isinstance(restored_doc, TokenizedDoc), "应该恢复为TokenizedDoc对象"
    assert restored_doc.get_tokenized_doc() == tokenized_doc, "恢复的分词结果应该与原始数据相同"

def test_empty_docs():
    """测试空文档和空查询的情况"""
    # 空文档列表
    assert compute_bm25_scores(["测试"], []) == [], "空文档列表应该返回空分数列表"
    
    # 空查询
    doc = TokenizedDoc(list(jieba.cut("测试文档")))
    scores = compute_bm25_scores([], [doc])
    assert len(scores) == 1, "应该返回与文档数量相同的分数"
    assert scores[0] == 0, "空查询应该返回0分"

def test_error_handling():
    """测试错误处理"""
    # 测试无效的缓存数据
    with pytest.raises(ValueError):
        TokenizedDoc.from_cache({})  # 缺少tokenized_doc字段
        
    with pytest.raises(ValueError):
        TokenizedDoc.from_cache({"wrong_key": []})  # 错误的键 