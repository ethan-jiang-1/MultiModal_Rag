import logging
import os
import msgpack  # 需要先 pip install msgpack
import json

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.common.vdb_base import get_ref_path
from mrag_vdb.rerank._bm25_cache import TokenizedDocBM25, get_cached_bm25_folder


def get_bm25_cache_path_for_document(doc_unique_id: str) -> str:
    """生成缓存文件路径"""
    doc_folder = get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        return os.path.join(doc_folder, f"bm25_content.msgpack")  # 使用.msgpack后缀
    return None


def get_or_create_bm25_for_document(doc_unique_id: str) -> TokenizedDocBM25:
    """
    基于文档元信息创建BM25对象
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        TokenizedDocBM25: BM25计算对象
        
    Raises:
        IOError: 文件读写失败时
        ValueError: 元信息格式不正确时
    """
    # 先检查是否有缓存
    cache_path = get_bm25_cache_path_for_document(doc_unique_id)
    if cache_path is not None:
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = msgpack.unpack(f)
                return TokenizedDocBM25.from_cache(cache_data)
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
        cached_bm25 = TokenizedDocBM25(tokenized_doc)
        
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