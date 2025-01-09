from typing import List
from dotenv import load_dotenv
import rich

# 加载环境变量
load_dotenv()

from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.query.query2section_raw import query2section_raw_on_rag_context
from mrag_vdb.rerank._hybrid_rerank_section import hybrid_rerank_rrf
from mrag_vdb.dto.rag_context import RagContext
from mrag_vdb.dto.rag_input import RagInput

WEIGHT_DISTANCE = 0
WEIGHT_RERANK = 8
WEIFHT_BM25 = 1

def query2sortedsections_reranked(rag_context: RagContext,
                                  scored_sections_raw: List[ScoredRecoveredSection]) -> List[ScoredRecoveredSection]:
    distance_weight = WEIGHT_DISTANCE
    rerank_weight = WEIGHT_RERANK
    bm25_weight = WEIFHT_BM25

    sorted_sections_reranked = hybrid_rerank_rrf(rag_context.get_refined_query(), 
                                                 scored_sections_raw, 
                                                 distance_weight=distance_weight, 
                                                 rerank_weight=rerank_weight, 
                                                 bm25_weight=bm25_weight)
    return sorted_sections_reranked

if __name__ == "__main__":
    setup_logger_handlers()

    def _truncate_string(s: str, max_length: int) -> str:
        if len(s) > max_length:
            return s[:max_length - 3] + '...'  # 留出 3 个字符的空间给 '...'
        return s
    
    rag_input = RagInput(query="神经网络 中央处理器", preferred_kbnames=["papers"], limit_raw=10)
    rag_context = RagContext(input=rag_input)

    scored_sections_raw = query2section_raw_on_rag_context(rag_context)
    scored_sections_rrf = query2sortedsections_reranked(rag_context, scored_sections_raw)

    print("query", rag_input.query)
    rich.print([(item.score_rrf, item.score, _truncate_string(item.content, 80)) for item in scored_sections_rrf])
