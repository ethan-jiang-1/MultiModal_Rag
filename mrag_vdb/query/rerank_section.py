from typing import Any, List, Tuple
from dotenv import load_dotenv
import sys
import os
import jieba
from rank_bm25 import BM25Okapi
import dashscope
import logging
import rich

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection

MAX_DOC_LEN = 3000  # max len restricted by RERANK

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


def bm25_reorder(query_str: str, documents: List[str], top_n: int = None):
    """
    使用 BM25 对文档进行排序，并返回相关性分数。
    
    :param query_str: 查询字符串
    :param documents: 文档列表
    :param top_n: 返回的文档数（可选，默认为所有文档）
    :return: 按 BM25 分数排序后的文档列表，每个元素包含索引、文档和相关性分数
    """
    # 对查询进行分词
    query_words = list(jieba.cut(query_str))

    # 文档截断到 3000 个字符，并对每个文档分词
    documents = [doc[:MAX_DOC_LEN] for doc in documents]
    tokenized_documents = [list(jieba.cut(doc)) for doc in documents]

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

    
def dashscope_rerank(query_str:str, documents: List[str], top_n: int = None):
    model = "gte-rerank"
    api_key = os.getenv("DASHSCOPE_API_KEY")

    documents = [item[:MAX_DOC_LEN] for item in documents]

    logging.info("start to call dashscope TextReRank...")
    ds_results = dashscope.TextReRank.call(
                model=model,
                top_n=top_n,
                query=query_str,
                documents=documents,
                api_key=api_key,
                return_documents=True,
            )
    
    results_items = ds_results.output.results
    rerank_results = []
    for i, results_item in enumerate(results_items):
        rerank_results.append({
            "index": i,
            "document": results_item["document"]["text"],
            "relevance_score": round(float(results_item["relevance_score"]), 5)
        })
    rerank_results = normalize_scores(rerank_results, 0, 1)
    return rerank_results

def normalize_scores(results, min_score, max_score):
    """
    对分数进行归一化，将所有分数映射到 [0, 1]
    """
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

def assign_score_rrf_score(sorted_rrf_scores, sorted_sections):
    for srs in sorted_rrf_scores:
        matched = False
        for ss in sorted_sections:
            if ss.content.startswith(srs["document"]):
                ss.score_rrf = round(srs["rrf_score"], 5)
                matched = True
                break
        if not matched:
            logging.error(f"find no match for {srs}")

def rerank_rrf(query_str: str, scored_sections: List[ScoredRecoveredSection], distance_weight=1, rerank_weight=8, bm25_weight=1) -> List[ScoredRecoveredSection]:
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

    # 获取其他来源的排序结果
    bm25_results = bm25_reorder(query_str, indexed_documents)
    rerank_results = dashscope_rerank(query_str, indexed_documents)

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
    from mrag_vdb.utils.utili_embedding import get_text_embedding
    from mrag_vdb.utils.util_logging import setup_logger_handlers
    from mrag_vdb.common.vdb_base import VDB_PATH
    from mrag_vdb.common.vdb_base import QdrantClientContextManager
    from mrag_vdb.query.query2section_raw import query_initial_points, recover_scored_sections_from_chunk_from_vdb

    setup_logger_handlers()

    query_str = "神经网络 中央处理器"
    #query_str = "Intel(R) Xeon(R)"
    collection_name = "papers"
    limit = 10

    def _truncate_string(s: str, max_length: int) -> str:
        if len(s) > max_length:
            return s[:max_length - 3] + '...'  # 留出 3 个字符的空间给 '...'
        return s

    with QdrantClientContextManager(path=VDB_PATH) as client:
        query_vector = get_text_embedding(query_str)

        initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=limit)
        
        merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

        rich.print(merged_scored_sections)

    distance_weight=0
    rerank_weight=8
    bm25_weight=1
    sorted_sections_rrf = rerank_rrf(query_str, merged_scored_sections, distance_weight=distance_weight, rerank_weight=rerank_weight, bm25_weight=bm25_weight)
    #rich.print(sorted_sections_rrf)
    print()
    print("len after initial query", len(initial_scored_chunks))   
    print("len after merge sections", len(merged_scored_sections))
    print("len after merge rrf", len(sorted_sections_rrf))
    print()
    print("query", query_str)
    rich.print([(item.score_rrf, item.score, _truncate_string(item.content, 80)) for item in sorted_sections_rrf])
