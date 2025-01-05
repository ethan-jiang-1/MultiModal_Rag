from typing import List, TypedDict

class RerankResult(TypedDict):
    """排序结果类型"""
    index: int
    document: str
    relevance_score: float


class RrfRerankResult(TypedDict):
    """排序结果类型"""
    index: int
    document: str
    rrf_score: float


def normalize_scores(results: List[RerankResult], min_score: float, max_score: float) -> List[RerankResult]:
    """
    对分数进行归一化，将所有分数映射到 [0, 1]
    """
    for r in results:
        if max_score > min_score:
            r['relevance_score'] = round((r['relevance_score'] - min_score) / (max_score - min_score), 5)
        else:
            r['relevance_score'] = 1.0  # 所有分数相等时，设为1.0
    return results