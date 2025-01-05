import logging
import os
import msgpack  # 需要先 pip install msgpack
import hashlib
import json
from typing import List, Optional
#from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.query._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.common.vdb_base import get_ref_path
from mrag_vdb.query._bm25_cache import CachedBM25
from mrag_vdb.query._rerank_base import RerankResult, normalize_scores


def _get_cached_bm25_folder(doc_unique_id: str) -> Optional[str]:
    """
    获取BM25缓存文件夹路径
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        Optional[str]: 缓存文件夹路径，如果创建失败则返回None
    """
    ref_path = get_ref_path()
    doc_ref_dir = os.path.join(ref_path, doc_unique_id)
    if os.path.isdir(doc_ref_dir):
        cached_bm25_folder = os.path.join(doc_ref_dir, "cached_bm25")
        os.makedirs(cached_bm25_folder, exist_ok=True)
        if os.path.isdir(cached_bm25_folder):
            return cached_bm25_folder
    return None

def _get_bm25_cache_path_for_section(doc_unique_id: str, section_content: str) -> str:
    """生成缓存文件路径"""
    doc_folder = _get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        content_hash = hashlib.md5(section_content.encode()).hexdigest()
        return os.path.join(doc_folder, f"bm25_{content_hash}.msgpack")  # 使用.msgpack后缀
    return None

def _get_bm25_cache_path_for_document(doc_unique_id: str) -> str:
    """生成缓存文件路径"""
    doc_folder = _get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        return os.path.join(doc_folder, f"bm25_content.msgpack")  # 使用.msgpack后缀
    return None

def get_or_create_bm25_for_section(section_content: str, doc_unique_id: Optional[str] = None) -> CachedBM25:
    """
    获取或创建BM25对象
    
    Args:
        section_content: 文档内容
        doc_id: 文档唯一标识符
        
    Returns:
        CachedBM25: BM25计算对象
        
    Raises:
        ValueError: 文档内容为空时
        IOError: 缓存文件读写失败时
        msgpack.UnpackException: 缓存文件损坏时
    """
    if not section_content:
        raise ValueError("Document content cannot be empty")
        
    if doc_unique_id:
        cache_path = _get_bm25_cache_path_for_section(doc_unique_id, section_content)
        if cache_path is not None:
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:  # 注意这里用'rb'模式
                        cache_data = msgpack.unpack(f)
                    return CachedBM25.from_cache(cache_data)
                except msgpack.UnpackException as e:
                    logging.warning(f"Failed to decode cached BM25 for document {doc_unique_id}: {e}")
                except ValueError as e:
                    logging.warning(f"Invalid cache data for document {doc_unique_id}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error loading BM25 cache for document {doc_unique_id}: {e}")
            
            # 创建新的BM25对象
            tokenized_doc = jieba_cut_without_stopwords(section_content)
            cached_bm25 = CachedBM25(tokenized_doc)
            
            # 保存到缓存
            try:
                with open(cache_path, 'wb') as f:  # 注意这里用'wb'模式
                    msgpack.pack(cached_bm25.to_cache(), f)
            except IOError as e:
                logging.error(f"Failed to cache BM25 for document {doc_unique_id}: {e}")
                raise
            
            return cached_bm25
    
    return CachedBM25(jieba_cut_without_stopwords(section_content))

def get_or_create_bm25_for_document(doc_unique_id: str) -> CachedBM25:
    """
    基于文档元信息创建BM25对象
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        CachedBM25: BM25计算对象
        
    Raises:
        IOError: 文件读写失败时
        ValueError: 元信息格式不正确时
    """
    # 先检查是否有缓存
    cache_path = _get_bm25_cache_path_for_document(doc_unique_id)
    if cache_path is not None:
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = msgpack.unpack(f)
                return CachedBM25.from_cache(cache_data)
            except Exception as e:
                logging.warning(f"Failed to load cached BM25 for document {doc_unique_id}: {e}")
    
    # 读取文档元信息
    ref_path = get_ref_path()
    meta_path = os.path.join(ref_path, doc_unique_id, "doc_meta.json")
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            doc_meta = json.load(f)
        
        if 'doc_summary' not in doc_meta:
            raise ValueError(f"No doc_summary found in meta file for document {doc_unique_id}")
            
        # 使用doc_summary创建BM25对象
        tokenized_doc = jieba_cut_without_stopwords(doc_meta['doc_summary'])
        cached_bm25 = CachedBM25(tokenized_doc)
        
        # 保存到缓存
        if cache_path:
            try:
                with open(cache_path, 'wb') as f:
                    msgpack.pack(cached_bm25.to_cache(), f)
            except Exception as e:
                logging.warning(f"Failed to cache BM25 for document {doc_unique_id}: {e}")
        
        return cached_bm25
        
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Failed to read meta file for document {doc_unique_id}: {e}")
        raise

def bm25_reorder(
    query_str: str, 
    sections: List[str], 
    indexed_doc_unique_ids: Optional[List[str]] = None, 
    top_n: Optional[int] = None
) -> List[RerankResult]:
    """
    使用带缓存的BM25对文档进行排序
    
    Args:
        query_str: 查询字符串
        documents: 待排序的文档列表
        indexed_doc_unique_ids: 文档ID列表，用于缓存查找
        top_n: 返回前n个结果
        
    Returns:
        List[BM25Result]: 排序后的结果列表
        
    Raises:
        ValueError: 参数验证失败时
    """
    if not query_str:
        raise ValueError("Query string cannot be empty")
    
    if not sections:
        raise ValueError("Documents list cannot be empty")
        
    if indexed_doc_unique_ids and len(sections) != len(indexed_doc_unique_ids):
        raise ValueError("Documents and document IDs must have the same length")
        
    if top_n is not None and top_n <= 0:
        raise ValueError("top_n must be positive")
        
    query_words = jieba_cut_without_stopwords(query_str)
    bm25_results: List[RerankResult] = []

    for i, (section, doc_id) in enumerate(zip(sections, indexed_doc_unique_ids or [None] * len(sections))):
        cached_bm25 = get_or_create_bm25_for_section(section, doc_id)
        score = cached_bm25.get_scores(query_words)[0]
        
        bm25_results.append({
            "index": i,
            "document": section,
            "relevance_score": round(float(score), 5)
        })

    bm25_results = normalize_scores(bm25_results, -20, 20)
    bm25_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return bm25_results[:top_n] if top_n else bm25_results

if __name__ == "__main__":
    # 测试文档
    test_sections = [
        "人工智能是计算机科学的一个重要分支，主要研究如何让计算机模拟人类智能。",
        "机器学习是人工智能的核心技术之一，通过数据训练来实现智能决策。",
        "深度学习是机器学习的一个分支，使用多层神经网络来学习数据特征。"
    ]
    
    # 模拟文档ID
    test_doc_ids = [
        "mrag_1__座椅STO间隙_P1_28b5d804",
        "mrag_1__座椅STO间隙_P1_28b5d804",
        "mrag_1__座椅STO间隙_P1_28b5d804"
    ]
    
    # 测试查询
    test_query = "人工智能机器学习"
    
    print("测试文档:")
    for i, doc in enumerate(test_sections):
        print(f"{i+1}. {doc}")
    print("\n查询语句:", test_query)
    
    # 执行BM25排序
    results = bm25_reorder(
        query_str=test_query,
        sections=test_sections,
        indexed_doc_unique_ids=test_doc_ids
    )
    
    print("\n排序结果:")
    for i, result in enumerate(results):
        print(f"\n第{i+1}名:")
        print(f"文档: {result['document']}")
        print(f"相关度分数: {result['relevance_score']}")