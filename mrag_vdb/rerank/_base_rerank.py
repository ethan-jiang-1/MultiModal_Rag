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
    """对搜索结果的相关性分数进行归一化处理，将分数映射到 [0, 1] 区间内。

    这个函数使用最小-最大归一化（Min-Max Normalization）方法，公式为：
    normalized_score = (original_score - min_score) / (max_score - min_score)

    Args:
        results: 包含排序结果的列表，每个元素都是 RerankResult 类型的字典
        min_score: 所有分数中的最小值
        max_score: 所有分数中的最大值

    Returns:
        List[RerankResult]: 返回归一化后的结果列表，分数被映射到 [0, 1] 区间

    特殊情况：
        - 当 max_score = min_score 时（所有分数相等），所有分数将被设置为 1.0
        - 归一化后的分数保留 5 位小数

    使用示例：
        >>> results = [
        ...     {"index": 0, "document": "doc1", "relevance_score": 100},
        ...     {"index": 1, "document": "doc2", "relevance_score": 200},
        ...     {"index": 2, "document": "doc3", "relevance_score": 300}
        ... ]
        >>> min_score, max_score = 100, 300
        >>> normalized = normalize_scores(results, min_score, max_score)
        >>> # 结果将变为 [0.0, 0.5, 1.0]
    """
    for r in results:
        if max_score > min_score:
            r['relevance_score'] = round((r['relevance_score'] - min_score) / (max_score - min_score), 5)
        else:
            r['relevance_score'] = 1.0  # 所有分数相等时，设为1.0
    return results