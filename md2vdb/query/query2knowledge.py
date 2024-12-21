from typing import List
from dotenv import load_dotenv
import sys
#import logging
import rich

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.query.recover_section_for_query import ScoredSection
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.query.query2section import query2section_on_multiple_collection
from md2vdb.query.rerank_section import rerank_rrf

def find_collection_names(query: str) -> List[str]:
    return ["papers"]

def query_rewerite(query: str, collection_names: List[str]) -> str:
    return query 

def query2sortedsections(query: str, limit: int = 10) -> List[ScoredSection]:
    collection_names = find_collection_names(query)
    query = query_rewerite(query, collection_names)

    merged_scored_sections = query2section_on_multiple_collection(collection_names, query, limit=limit)

    distance_weight=0
    rerank_weight=8
    bm25_weight=1
    sorted_sections_rrf = rerank_rrf(query_str, merged_scored_sections, distance_weight=distance_weight, rerank_weight=rerank_weight, bm25_weight=bm25_weight)
    return sorted_sections_rrf

if __name__ == "__main__":
    setup_logger_handlers()

    def _truncate_string(s: str, max_length: int) -> str:
        if len(s) > max_length:
            return s[:max_length - 3] + '...'  # 留出 3 个字符的空间给 '...'
        return s
    
    query_str = "神经网络 中央处理器"
    sorted_sections_rrf = query2sortedsections(query_str)

    print("query", query_str)
    rich.print([(item.score_rrf, item.score, _truncate_string(item.content, 80)) for item in sorted_sections_rrf])
