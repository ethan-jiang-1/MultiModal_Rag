from typing import Any, List, Tuple
from dotenv import load_dotenv
import logging
import rich

from mrag_vdb.rerank._base_rerank import RerankResult, RrfRerankResult

# 加载环境变量
load_dotenv()


from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.rerank._base_rerank import normalize_scores
from mrag_vdb.rerank._bm25_reorder import bm25_reorder

def convert_to_documents_and_distance_results(scored_sections: List[ScoredRecoveredSection]) -> Tuple[List[str], List[ScoredRecoveredSection], List[Any]]:
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
            "relevance_score": round(relevance_score, 5)
        })

    distance_results = normalize_scores(distance_results, 0, 1)
    return indexed_documents, sorted_sections, distance_results
    
def embedding_rerank(query_str:str, documents: List[str], top_n: int = None) -> List[RerankResult]:
    from mrag_vdb.rerank._embeding_rerankers import qwen_gte_rerank, autodl_jina_rerank, jinaai_jina_rerank
    try:
        return autodl_jina_rerank(query_str, documents, top_n=top_n)
    except Exception as ex:
        logging.error(f"embedding_rerank exception occured(0): {ex}")

    try:
        return qwen_gte_rerank(query_str, documents, top_n=top_n)
    except Exception as ex:
        logging.error(f"embedding_rerank exception occured(1): {ex}")

    try:
        return jinaai_jina_rerank(query_str, documents, top_n=top_n)
    except Exception as ex:
        logging.error(f"embedding_rerank exception occured(2): {ex}")

    raise ValueError("no alive reranker")

def calculate_rrf_multiple(sources: List[Any], k: int = 60) -> List[RrfRerankResult]:
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

def assign_score_rrf_score(sorted_rrf_scores: List[dict], sorted_sections: List[ScoredRecoveredSection]) -> None:
    for srs in sorted_rrf_scores:
        matched = False
        for ss in sorted_sections:
            if ss.content.startswith(srs["document"]):
                ss.score_rrf = round(srs["rrf_score"], 5)
                matched = True
                break
        if not matched:
            logging.error(f"find no match for {srs}")

def hybrid_rerank_rrf(query_str: str, 
                      scored_sections: List[ScoredRecoveredSection], 
                      distance_weight=1, 
                      rerank_weight=8, 
                      bm25_weight=1) -> List[ScoredRecoveredSection]:
    """
    使用 RRF 融合多个排序来源，并对不同来源应用权重。
    
    :param query_str: 查询字符串
    :param scored_sections: ScoredSection 数据列表
    :param distance_weight: 距离排序的权重
    :param rerank_weight: ReRank 排序的权重
    :param bm25_weight: BM25 排序的权重
    :return: 融合后的排序结果，按照 RRF 分数从高到低排序
    """
    # 转换 scored_sections 为文档列表和距离结果
    indexed_documents, sorted_sections, distance_results = convert_to_documents_and_distance_results(scored_sections)

    indexed_doc_unique_ids = [item.doc_unique_id for item in sorted_sections]

    # 获取其他来源的排序结果
    bm25_results = bm25_reorder(query_str, indexed_documents, indexed_doc_unique_ids=indexed_doc_unique_ids)
    rerank_results = embedding_rerank(query_str, indexed_documents)

    logging.info(f"query_str: {query_str} rerank scores:")
    logging.info(f"{("distance_results", [item["relevance_score"] for item in distance_results], distance_weight)}")
    logging.info(f"{("bm25_results    ", [item["relevance_score"] for item in bm25_results], bm25_weight)}")
    logging.info(f"{("rerank_results  ", [item["relevance_score"] for item in rerank_results], rerank_weight)}")

    # 各来源及其权重
    sources = []
    if distance_weight > 0:
        sources.append((distance_results, distance_weight))
    if rerank_weight > 0:
        sources.append((rerank_results, rerank_weight))
    if bm25_weight > 0:
        sources.append((bm25_results, bm25_weight))

    # 计算 RRF 排序结果
    sorted_rrf_scores = calculate_rrf_multiple(sources)
    assign_score_rrf_score(sorted_rrf_scores, sorted_sections)
    sorted_sections_rrf = sorted(sorted_sections, key=lambda x: x.score_rrf, reverse=True)
    return sorted_sections_rrf


if __name__ == "__main__":
    from mrag_vdb.common.text_embedding import get_embedding_vec
    from mrag_vdb.utils.util_logging import setup_logger_handlers
    from mrag_vdb.common.vdb_base import get_vdb_path
    from mrag_vdb.common.vdb_base import QdrantClientContextManager
    from mrag_vdb.query.query2section_raw import query_initial_points, recover_scored_sections_from_chunk_from_vdb

    setup_logger_handlers()

    query_str = "神经网络 中央处理器 network cpu AI 卷积"
    #query_str = "Intel(R) Xeon(R)"
    collection_name = "papers"
    limit = 10

    def _truncate_string(s: str, max_length: int) -> str:
        if len(s) > max_length:
            return s[:max_length - 3] + '...'  # 留出 3 个字符的空间给 '...'
        return s

    with QdrantClientContextManager(path=get_vdb_path()) as client:
        query_vector = get_embedding_vec(query_str)

        initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=limit)
        
        merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

        rich.print(merged_scored_sections)

    distance_weight=0
    rerank_weight=8
    bm25_weight=1
    sorted_sections_rrf = hybrid_rerank_rrf(query_str, merged_scored_sections, distance_weight=distance_weight, rerank_weight=rerank_weight, bm25_weight=bm25_weight)
    #rich.print(sorted_sections_rrf)
    print()
    print("len after initial query", len(initial_scored_chunks))   
    print("len after merge sections", len(merged_scored_sections))
    print("len after merge rrf", len(sorted_sections_rrf))
    print()
    print("query", query_str)
    rich.print([(item.score_rrf, item.score, _truncate_string(item.content, 80)) for item in sorted_sections_rrf])
