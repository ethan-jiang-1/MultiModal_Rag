from typing import List
from dotenv import load_dotenv
import sys
import rich

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection
from mrag_vdb.query._hybrid_rerank_section import hybrid_rerank_rrf

WEIGHT_DISTANCE = 0
WEIGHT_RERANK = 8
WEIFHT_BM25 = 1

def query2sortedsections_reranked(query: str, 
                                  scored_sections_raw: List[ScoredRecoveredSection]) -> List[ScoredRecoveredSection]:
    distance_weight = WEIGHT_DISTANCE
    rerank_weight = WEIGHT_RERANK
    bm25_weight = WEIFHT_BM25

    sorted_sections_reranked = hybrid_rerank_rrf(query, scored_sections_raw, distance_weight=distance_weight, rerank_weight=rerank_weight, bm25_weight=bm25_weight)
    return sorted_sections_reranked

if __name__ == "__main__":
    setup_logger_handlers()

    def _truncate_string(s: str, max_length: int) -> str:
        if len(s) > max_length:
            return s[:max_length - 3] + '...'  # 留出 3 个字符的空间给 '...'
        return s
    
    query_str = "神经网络 中央处理器"
    collection_names =["papers"]
    limit = 10

    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query_str, limit=limit)
    scored_sections_rrf = query2sortedsections_reranked(query_str, scored_sections_raw)

    print("query", query_str)
    rich.print([(item.score_rrf, item.score, _truncate_string(item.content, 80)) for item in scored_sections_rrf])
