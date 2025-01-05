from typing import List, Optional
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import os

# 加载环境变量
load_dotenv()

from mrag_vdb.query._embeding_rerankers import normalize_scores
from mrag_vdb.query._jieba_cutter import jieba_cut
from mrag_vdb.common.vdb_base import get_ref_path

# def _get_cached_md25_folder(doc_unique_id: str) -> str:
#     ref_path = get_ref_path()
#     doc_ref_dir = os.path.join(ref_path, doc_unique_id)
#     if os.path.isdir(doc_ref_dir):
#         cached_md25_folder = os.path.join(doc_ref_dir, "cached_md25")
#         os.makedirs(cached_md25_folder, exist_ok=True)
#         if os.path.isdir(cached_md25_folder):
#             return cached_md25_folder
#     return None

#def _cached_

def bm25_reorder(query_str: str, documents: List[str], indexed_doc_unique_ids: Optional[List[str]] = None, top_n: Optional[int] = None, ) -> List[dict]:
    """
    使用 BM25 对文档进行排序，并返回相关性分数。
    
    :param query_str: 查询字符串
    :param documents: 文档列表
    :param top_n: 返回的文档数（可选，默认为所有文档）
    :param indexed_doc_unique_ids: 文档的唯一标识列表
    :return: 按 BM25 分数排序后的文档列表，每个元素包含索引、文档和相关性分数
    """

    # 对查询进行分词
    query_words = jieba_cut(query_str)

    # 文档截断到 3000 个字符，并对每个文档分词
    tokenized_documents = [jieba_cut(doc) for doc in documents]

    # 创建 BM25 对象
    bm25_documents = BM25Okapi(tokenized_documents)

    # 计算 BM25 分数
    bm25_scores = bm25_documents.get_scores(query_words)

    # 构建结果列表
    bm25_results = []
    for i, score in enumerate(bm25_scores):
        bm25_results.append({
            "index": i,
            "document": documents[i],
            "relevance_score": round(float(score), 5)
        })

    # 归一化 BM25 分数到 [0, 1] 范围
    bm25_results = normalize_scores(bm25_results, 0, 1)

    # 按 BM25 分数排序
    bm25_results = sorted(bm25_results, key=lambda x: x["relevance_score"], reverse=True)

    return bm25_results