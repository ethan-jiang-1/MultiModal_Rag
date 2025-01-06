import pytest
import os
from mrag_vdb.rerank._bm25_cache_section import (
    get_bm25_cache_path_for_section,
    get_or_create_bm25_for_section
)

@pytest.fixture
def sample_doc_id():
    return "test_doc_123"

@pytest.fixture
def sample_section_content():
    return """
    机器学习是人工智能的一个分支，主要研究计算机怎样模拟或实现人类的学习行为。
    机器学习算法是一类从数据中自动分析获得规律，并利用规律对未知数据进行预测的算法。
    常见的机器学习算法包括监督学习、无监督学习和强化学习等。
    """

def test_get_bm25_cache_path(sample_doc_id, sample_section_content):
    """测试缓存路径生成"""
    cache_path = get_bm25_cache_path_for_section(sample_doc_id, sample_section_content)
    assert cache_path is not None
    assert cache_path.endswith(".msgpack")
    assert sample_doc_id in cache_path

def test_get_or_create_bm25_no_cache(sample_section_content):
    """测试不使用缓存创建BM25"""
    bm25 = get_or_create_bm25_for_section(sample_section_content)
    assert bm25 is not None
    
    # 测试搜索功能
    score = bm25.get_score("机器学习")
    assert isinstance(score, float)
    assert score > 0

def test_get_or_create_bm25_with_cache(sample_doc_id, sample_section_content):
    """测试使用缓存创建BM25"""
    # 首次创建（写入缓存）
    bm25_first = get_or_create_bm25_for_section(sample_section_content, sample_doc_id)
    first_score = bm25_first.get_score("机器学习")
    
    # 第二次创建（从缓存读取）
    bm25_second = get_or_create_bm25_for_section(sample_section_content, sample_doc_id)
    second_score = bm25_second.get_score("机器学习")
    
    # 验证两次得分一致
    assert abs(first_score - second_score) < 1e-6
    
    # 清理缓存文件
    cache_path = get_bm25_cache_path_for_section(sample_doc_id, sample_section_content)
    if os.path.exists(cache_path):
        os.remove(cache_path)

def test_get_or_create_bm25_empty_content():
    """测试空内容错误处理"""
    with pytest.raises(ValueError):
        get_or_create_bm25_for_section("")

def test_get_or_create_bm25_different_content(sample_doc_id):
    """测试不同内容生成不同的缓存"""
    content1 = "机器学习内容A"
    content2 = "机器学习内容B"
    
    bm25_1 = get_or_create_bm25_for_section(content1, sample_doc_id)
    bm25_2 = get_or_create_bm25_for_section(content2, sample_doc_id)
    
    # 验证两个内容的得分不同
    query = "机器学习"
    score1 = bm25_1.get_score(query)
    score2 = bm25_2.get_score(query)
    assert score1 != score2
    
    # 清理缓存文件
    cache_path1 = get_bm25_cache_path_for_section(sample_doc_id, content1)
    cache_path2 = get_bm25_cache_path_for_section(sample_doc_id, content2)
    for path in [cache_path1, cache_path2]:
        if os.path.exists(path):
            os.remove(path) 