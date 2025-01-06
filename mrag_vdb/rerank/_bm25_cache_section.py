import logging
import os
import msgpack  # 需要先 pip install msgpack
import hashlib

from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.rerank._bm25_cache import TokenizedDocBM25, get_cached_bm25_folder
from mrag_vdb.utils.util_logging import setup_logger_handlers


def get_bm25_cache_path_for_section(doc_unique_id: str, section_content: str) -> str:
    """生成缓存文件路径"""
    doc_folder = get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        content_hash = hashlib.md5(section_content.encode()).hexdigest()
        return os.path.join(doc_folder, f"bm25_{content_hash}.msgpack")  # 使用.msgpack后缀
    return None

def get_or_create_bm25_for_section(section_content: str, doc_unique_id: Optional[str] = None) -> TokenizedDocBM25:
    """
    获取或创建BM25对象
    
    Args:
        section_content: 文档内容
        doc_id: 文档唯一标识符
        
    Returns:
        TokenizedDocBM25: BM25计算对象
        
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
                    logging.info(f"Loaded cached BM25 for document {doc_unique_id} sec:{section_mem} from {cache_path}")
                    return TokenizedDocBM25.from_cache(cache_data)
                except msgpack.UnpackException as e:
                    logging.warning(f"Failed to decode cached BM25 for document {doc_unique_id}: {e}")
                except ValueError as e:
                    logging.warning(f"Invalid cache data for document {doc_unique_id}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error loading BM25 cache for document {doc_unique_id}: {e}")
            
            # 创建新的BM25对象
            tokenized_doc = jieba_cut_without_stopwords(section_content)
            tokenized_doc_bm25 = TokenizedDocBM25(tokenized_doc)
            
            # 保存到缓存
            try:
                with open(cache_path, 'wb') as f:  # 注意这里用'wb'模式
                    msgpack.pack(tokenized_doc_bm25.to_cache(), f)
                logging.info(f"Cached BM25 for document {doc_unique_id} sec:{section_mem} created at {cache_path}")
            except IOError as e:
                logging.error(f"Failed to cache BM25 for document {doc_unique_id}: {e}")
                raise
            
            return tokenized_doc_bm25
    
    logging.info(f"No cached BM25 found for document {doc_unique_id} sec:{section_mem}, creating new one")
    return TokenizedDocBM25(jieba_cut_without_stopwords(section_content))

if __name__ == "__main__":
    setup_logger_handlers()
    # 创建临时测试目录
    doc_id = "test_bm25_12345678"
    
    try:
        # 测试文档内容
        test_doc = """
        机器学习是人工智能的一个分支，主要研究计算机怎样模拟或实现人类的学习行为。
        机器学习算法是一类从数据中自动分析获得规律，并利用规律对未知数据进行预测的算法。
        常见的机器学习算法包括监督学习、无监督学习和强化学习等。
        """
        
        cache_path = get_bm25_cache_path_for_section(doc_id, test_doc)
        print(f"缓存路径: {cache_path}")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        
        # 测试场景1：不使用缓存
        print("测试1: 不使用缓存创建BM25")
        tdbm25_no_cache = get_or_create_bm25_for_section(test_doc)
        test_query = "什么是机器学习"
        score = tdbm25_no_cache.get_score(test_query)
        print(f"查询 '{test_query}' 的BM25得分: {score}\n")
        
        # 测试场景2：使用缓存
        print(f"测试2: 使用缓存创建BM25: {os.path.exists(cache_path)}")
        
        
        # 第一次调用：创建并缓存
        print("首次创建并缓存...")
        tdbm25_with_cache = get_or_create_bm25_for_section(test_doc, doc_id)
        score1 = tdbm25_with_cache.get_score(test_query)
        print(f"首次查询得分: {score1}")
        
        # 第二次调用：从缓存加载
        print("\n从缓存加载...")
        tdbm25_from_cache = get_or_create_bm25_for_section(test_doc, doc_id)
        score2 = tdbm25_from_cache.get_score(test_query)
        print(f"缓存加载后查询得分: {score2}")
        
        # 验证两次得分是否一致
        print(f"\n得分一致性检查: {'通过' if abs(score1 - score2) < 1e-10 else '失败'}")

    finally:
        # 清理临时目录
        os.remove(cache_path)
