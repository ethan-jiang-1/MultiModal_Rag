import os
import pytest
from mrag_vdb.rerank._bm25_cache_section import (
    get_bm25_cache_path_for_section as get_bm25_cache_path,
    get_or_create_bm25_for_section as get_or_create_bm25,
)

@pytest.fixture
def temp_cache_dir(tmp_path):
    """创建临时缓存目录"""
    cache_dir = tmp_path / "_ds_ref"  # 使用正确的目录名
    cache_dir.mkdir(parents=True)
    return cache_dir

@pytest.fixture
def mock_env_vars(monkeypatch, temp_cache_dir):
    """模拟环境变量"""
    monkeypatch.setenv("MRAG_CACHE_ROOT", str(temp_cache_dir))

def create_doc_dir(temp_cache_dir, doc_id):
    """创建文档目录及其缓存子目录"""
    doc_dir = os.path.join(temp_cache_dir, doc_id)
    os.makedirs(doc_dir, exist_ok=True)
    cache_dir = os.path.join(doc_dir, "cached_bm25")
    os.makedirs(cache_dir, exist_ok=True)
    return doc_dir

def test_get_bm25_cache_path(mock_env_vars, temp_cache_dir):
    """测试获取BM25缓存路径"""
    doc_id = "test_doc_123"
    content = "测试文档内容"
    
    # 创建文档目录
    create_doc_dir(temp_cache_dir, doc_id)
    
    cache_path = get_bm25_cache_path(doc_id, content)
    
    assert cache_path is not None
    assert isinstance(cache_path, str)
    assert str(temp_cache_dir) in cache_path
    assert doc_id in cache_path
    assert cache_path.endswith(".msgpack")

def test_get_or_create_bm25_no_cache(mock_env_vars, temp_cache_dir):
    """测试无缓存时创建BM25"""
    content = "这是一个测试文档"
    doc_id = "test_doc_no_cache"
    
    # 创建文档目录
    create_doc_dir(temp_cache_dir, doc_id)
    
    # 获取BM25对象
    bm25 = get_or_create_bm25(content, doc_id)
    assert bm25 is not None
    
    # 测试相关性计算
    query = "测试"
    score = bm25.get_score(query)
    assert isinstance(score, float)
    
    # 验证缓存文件已创建
    cache_path = get_bm25_cache_path(doc_id, content)
    assert os.path.exists(cache_path)

def test_get_or_create_bm25_with_cache(mock_env_vars, temp_cache_dir):
    """测试从缓存加载BM25"""
    content = "这是一个测试文档"
    doc_id = "test_doc_with_cache"
    
    # 创建文档目录
    create_doc_dir(temp_cache_dir, doc_id)
    
    # 首次创建
    bm25_original = get_or_create_bm25(content, doc_id)
    query = "测试"
    score_original = bm25_original.get_score(query)
    
    # 再次加载
    bm25_loaded = get_or_create_bm25(content, doc_id)
    score_loaded = bm25_loaded.get_score(query)
    
    # 验证结果一致
    assert score_original == score_loaded

def test_get_or_create_bm25_empty_content():
    """测试空内容处理"""
    with pytest.raises(ValueError):
        get_or_create_bm25("", "test_doc_empty")

def test_get_or_create_bm25_different_content(mock_env_vars, temp_cache_dir):
    """测试内容变化时的处理"""
    doc_id = "test_doc_diff"
    content1 = "这是第一个测试文档，包含一些独特的词语"
    content2 = "这是第二个测试文档，包含完全不同的内容"
    
    # 创建文档目录
    create_doc_dir(temp_cache_dir, doc_id)
    
    # 创建第一个BM25
    bm25_1 = get_or_create_bm25(content1, doc_id)
    query = "独特"  # 只在第一个文档中出现的词
    score1 = bm25_1.get_score(query)
    
    # 使用不同内容创建第二个BM25
    bm25_2 = get_or_create_bm25(content2, doc_id)
    score2 = bm25_2.get_score(query)
    
    # 内容不同，分数应该不同
    assert score1 != score2 