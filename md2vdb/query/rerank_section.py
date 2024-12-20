from typing import Any, List, Tuple
from dotenv import load_dotenv
import sys
import os
import jieba
from rank_bm25 import BM25Okapi
import dashscope

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.query.recover_section_for_query import ScoredSection

def convert_to_documents_and_distance_results(scored_sections: List[ScoredSection]) -> Tuple[List[str], List[ScoredSection], List[Any]]:
    """
    将 ScoredSection 数据转化为 documents 和 distance_results 格式。
    
    :param scored_sections: ScoredSection 数据的列表
    :return: documents 和 distance_results
    """
    # 按照 score 从高到低排序
    sorted_sections = sorted(scored_sections, key=lambda x: x.score, reverse=True)

    # 转换为 documents 和 distance_results
    indexed_documents = []
    distance_results = []
    
    for ndx, section in enumerate(sorted_sections):
        # 提取主要信息
        document_content = section.content
        relevance_score = section.score

        # 添加到 documents 列表
        indexed_documents.append(document_content)

        # 构建 distance_results 的每个条目
        distance_results.append({
            "index": ndx,  # 当前的顺序
            "document": document_content,
            "relevance_score": relevance_score
        })

    return indexed_documents, sorted_sections, distance_results

def bm25_rerank(query_str:str, documents: List[str], top_n: int = None):

    query_words = list(jieba.cut(query_str))

    documents = [item[:3000] for item in documents]
    
    documents_tokens = []
    for document in documents:
        document_words = list(jieba.cut(document))
        document_tokens = BM25Okapi(document_words)
        documents_tokens.append(document_tokens)

    bm25_documents = BM25Okapi(documents)
    bm25_scores = bm25_documents.get_scores(query_words)

    results = []
    for i, score in enumerate(bm25_scores):
        results.append({
            "index": i,
            "document": documents[i],
            "relevance_score": float(score)
        })

    return results
    
def dashscope_rerank(query_str:str, documents: List[str], top_n: int = None):
    model = "gte-rerank"
    api_key = os.getenv("DASHSCOPE_API_KEY")

    documents = [item[:3000] for item in documents]

    ds_results = dashscope.TextReRank.call(
                model=model,
                top_n=top_n,
                query=query_str,
                documents=documents,
                api_key=api_key,
                return_documents=True,
            )
    
    results_items = ds_results.output.results
    results = [dict(item) for item in results_items]
    return results

def rerank_rrf(query_str: str, scored_sections: List[ScoredSection], distance_weight=1, jina_weight=8, bm25_weight=2):
    """
    使用 RRF 融合多个排序来源，并对不同来源应用权重。
    
    :param query_str: 查询字符串
    :param scored_sections: ScoredSection 数据列表
    :param distance_weight: 距离排序的权重
    :param jina_weight: Jina 排序的权重
    :param bm25_weight: BM25 排序的权重
    :return: 融合后的排序结果，按照 RRF 分数从高到低排序
    """
    # 转换 scored_sections 为文档列表和距离结果
    indexed_documents, sorted_sections, distance_results_org = convert_to_documents_and_distance_results(scored_sections)

    # 获取其他来源的排序结果
    bm25_results_org = bm25_rerank(query_str, indexed_documents)
    rerank_results_org = dashscope_rerank(query_str, indexed_documents)

    distance_results = normalize_scores(distance_results_org, 0, 1)
    bm25_results = normalize_scores(bm25_results_org, 0, 10)
    rerank_results = normalize_scores(rerank_results_org, 0, 1)

    # 各来源及其权重
    sources = [
        (distance_results, distance_weight),
        (rerank_results, jina_weight),
        (bm25_results, bm25_weight)
    ]

    # 计算 RRF 排序结果
    sorted_rrf_scores = calculate_rrf_multiple(sources)
    return sorted_rrf_scores

def normalize_scores(results, min_score, max_score):
    """
    对分数进行归一化，将所有分数映射到 [0, 1]
    """
    #scores = [r['relevance_score'] for r in results]
    #max_score = max(scores)
    #min_score = min(scores)

    for r in results:
        if max_score > min_score:
            r['relevance_score'] = (r['relevance_score'] - min_score) / (max_score - min_score)
        else:
            r['relevance_score'] = 1.0  # 所有分数相等时，设为1.0
    return results

def calculate_rrf_multiple(sources: List[Any], k: int = 60):
    """
    使用 RRF 融合多个排序来源 (e.g., BM25, distance, re-rank) 的结果，应用权重。
    
    :param sources: 一个列表，每个元素是一个排序来源及其权重，来源是一个排序结果的列表。
                    格式为 (source, weight)，其中 source 是一个列表，格式为：
                    [{"index": int, "document": str, "relevance_score": float}, ...]
    :param k: RRF 超参数，默认值为 60
    :return: 融合后的排序结果，按照 RRF 分数从高到低排序
    """
    # 创建每个来源的排名映射
    rank_mappings = []
    weights = []
    for source, weight in sources:
        rank_mapping = {doc["index"]: rank for rank, doc in enumerate(source, start=1)}
        rank_mappings.append(rank_mapping)
        weights.append(weight)

    # 获取所有唯一的文档索引
    all_indices = set()
    for rank_mapping in rank_mappings:
        all_indices.update(rank_mapping.keys())

    # 计算 RRF 分数
    rrf_scores = []
    for idx in all_indices:
        # 累计每个来源的加权 RRF 分数
        rrf_score = 0
        for rank_mapping, weight in zip(rank_mappings, weights):
            rank = rank_mapping.get(idx, float('inf'))  # 如果文档不在某个来源中，默认排名为无穷大
            rrf_score += weight * (1 / (k + rank))  # 权重影响

        # 获取文档内容（假设所有来源的文档内容一致，取第一个非空内容即可）
        document = None
        for source, _ in sources:
            doc = next((d for d in source if d["index"] == idx), None)
            if doc:
                document = doc["document"]
                break

        # 记录结果
        rrf_scores.append({
            "index": idx,
            "document": document,
            "rrf_score": rrf_score
        })

    # 按照 RRF 分数从高到低排序
    sorted_rrf_scores = sorted(rrf_scores, key=lambda x: x["rrf_score"], reverse=True)
    return sorted_rrf_scores


if __name__ == "__main__":
    import rich
    from md2vdb.utils.utili_embedding import get_text_embedding
    from md2vdb.utils.util_logging import setup_logger_handlers
    from md2vdb.common.vdb_base import VDB_PATH
    from md2vdb.query.query_bsae import QdrantClientContextManager
    from md2vdb.query.query2section import query_initial_points, recover_scored_sections_from_chunk_from_vdb

    setup_logger_handlers()

    #query_str = "神经网络"
    query_str = "Intel(R) Xeon(R)"
    collection_name = "papers"
    limit = 10


    with QdrantClientContextManager(path=VDB_PATH) as client:
        query_vector = get_text_embedding(query_str)

        initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=limit)

        merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

        rich.print(merged_scored_sections)

    result = rerank_rrf(query_str, merged_scored_sections)
    rich.print(result)
