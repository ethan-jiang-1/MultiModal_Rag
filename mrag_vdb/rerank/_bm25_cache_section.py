import logging
import os
import msgpack  # 需要先 pip install msgpack
import hashlib

from typing import Optional  # , List

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.rerank._bm25_cache import TokenizedDoc, get_cached_bm25_folder, compute_bm25_scores
from mrag_vdb.utils.util_logging import setup_logger_handlers


def get_bm25_cache_path_for_section(doc_unique_id: str, section_content: str) -> Optional[str]:
    """
    生成缓存文件路径
    
    Args:
        doc_unique_id: 文档唯一标识符
        section_content: 文档内容
        
    Returns:
        Optional[str]: 缓存文件路径，如果无法创建则返回None
    """
    doc_folder = get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        content_hash = hashlib.md5(section_content.encode()).hexdigest()
        return os.path.join(doc_folder, f"bm25_{content_hash}.msgpack")  # 使用.msgpack后缀
    return None

def get_or_create_tokenized_doc_for_section(section_content: str, doc_unique_id: Optional[str] = None) -> TokenizedDoc:
    """
    获取或创建预分词文档对象
    
    Args:
        section_content: 文档内容
        doc_id: 文档唯一标识符
        
    Returns:
        TokenizedDoc: 预分词文档对象
        
    Raises:
        ValueError: 文档内容为空时
        IOError: 缓存文件读写失败时
        msgpack.UnpackException: 缓存文件损坏时
    """
    if not section_content:
        raise ValueError("Document content cannot be empty")
    
    section_mem = '"'+ section_content[:25].replace("\n", " ") + "..." + '"'

    if doc_unique_id:
        cache_path = get_bm25_cache_path_for_section(doc_unique_id, section_content)
        if cache_path is not None:
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:  # 注意这里用'rb'模式
                        cache_data = msgpack.unpack(f)
                    logging.info(f"Loaded cached TokenizedDoc for document {doc_unique_id} sec:{section_mem} from {cache_path}")
                    return TokenizedDoc.from_cache(cache_data)
                except msgpack.UnpackException as e:
                    logging.warning(f"Failed to decode cached TokenizedDoc for document {doc_unique_id}: {e}")
                except ValueError as e:
                    logging.warning(f"Invalid cache data for document {doc_unique_id}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error loading TokenizedDoc cache for document {doc_unique_id}: {e}")
            
            # 创建新的TokenizedDoc对象
            tokenized_doc = jieba_cut_without_stopwords(section_content)
            tokenized_doc_obj = TokenizedDoc(tokenized_doc)
            
            # 保存到缓存
            try:
                with open(cache_path, 'wb') as f:  # 注意这里用'wb'模式
                    msgpack.pack(tokenized_doc_obj.to_cache(), f)
                logging.info(f"Cached TokenizedDoc for document {doc_unique_id} sec:{section_mem} created at {cache_path}")
            except IOError as e:
                logging.error(f"Failed to cache TokenizedDoc for document {doc_unique_id}: {e}")
                raise
            
            return tokenized_doc_obj
    
    logging.info(f"No cached TokenizedDoc found for document {doc_unique_id} sec:{section_mem}, creating new one")
    return TokenizedDoc(jieba_cut_without_stopwords(section_content))

if __name__ == "__main__":
    setup_logger_handlers()
    # 创建临时测试目录
    doc_id = "test_bm25_12345678"
    
    try:
        # 测试文档内容
        test_docs = [
            """机器学习是人工智能的一个分支，主要研究计算机怎样模拟或实现人类的学习行为。
            机器学习算法是一类从数据中自动分析获得规律，并利用规律对未知数据进行预测的算法。
            常见的机器学习算法包括监督学习、无监督学习和强化学习等。""",
            
            """自然语言处理是计算机科学领域与人工智能领域中的一个重要方向。
            它研究能实现人与计算机之间用自然语言进行有效通信的各种理论和方法。
            自然语言处理是一门融语言学、计算机科学、数学于一体的科学。""",
            
            """深度学习是机器学习的分支，是一种以人工神经网络为架构，
            对数据进行表征学习的算法。深度学习是机器学习中一种基于对数据进行表征学习的方法。"""
        ]
        
        # 测试场景1：不使用缓存
        print("测试1: 不使用缓存创建TokenizedDoc")
        docs_no_cache = [get_or_create_tokenized_doc_for_section(doc) for doc in test_docs]
        test_queries = [
            ["机器学习", "算法"],
            ["自然语言", "处理"],
            ["深度", "学习"]
        ]
        
        for query in test_queries:
            scores = compute_bm25_scores(query, docs_no_cache)
            print(f"\n查询 '{' '.join(query)}' 的BM25得分:")
            for i, score in enumerate(scores):
                print(f"文档{i+1}: {score:.4f}")
        
        # 测试场景2：使用缓存
        print("\n测试2: 使用缓存")
        
        # 第一次调用：创建并缓存
        print("首次创建并缓存...")
        docs_with_cache = []
        cache_paths = []  # 存储缓存路径用于清理
        
        for i, doc in enumerate(test_docs):
            doc_unique_id = f"{doc_id}_{i}"
            cache_path = get_bm25_cache_path_for_section(doc_unique_id, doc)
            if cache_path is not None:
                cache_paths.append(cache_path)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
            docs_with_cache.append(get_or_create_tokenized_doc_for_section(doc, doc_unique_id))
        
        original_scores = []
        for query in test_queries:
            scores = compute_bm25_scores(query, docs_with_cache)
            original_scores.append(scores)
            print(f"\n查询 '{' '.join(query)}' 的原始BM25得分:")
            for i, score in enumerate(scores):
                print(f"文档{i+1}: {score:.4f}")
        
        # 第二次调用：从缓存加载
        print("\n从缓存加载...")
        docs_from_cache = []
        for i, doc in enumerate(test_docs):
            doc_unique_id = f"{doc_id}_{i}"
            docs_from_cache.append(get_or_create_tokenized_doc_for_section(doc, doc_unique_id))
        
        # 验证得分一致性
        print("\n验证缓存前后得分一致性:")
        for query_idx, query in enumerate(test_queries):
            cached_scores = compute_bm25_scores(query, docs_from_cache)
            print(f"\n查询: '{' '.join(query)}'")
            for doc_idx, (orig_score, cached_score) in enumerate(zip(original_scores[query_idx], cached_scores)):
                print(f"文档{doc_idx+1} - 原始得分: {orig_score:.4f}, 缓存后得分: {cached_score:.4f}")
                print(f"得分一致: {abs(orig_score - cached_score) < 1e-6}")

    finally:
        # 清理临时文件
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                os.remove(cache_path)
