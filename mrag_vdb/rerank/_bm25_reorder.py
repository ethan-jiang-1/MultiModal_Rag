#import logging
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.rerank._base_rerank import RerankResult, normalize_scores 
from mrag_vdb.rerank._bm25_cache_section import get_or_create_tokenized_doc_for_section
from mrag_vdb.rerank._bm25_cache import compute_bm25_scores

def bm25_reorder(
    query_str: str, 
    sections: List[str], 
    indexed_doc_unique_ids: Optional[List[str]] = None, 
    top_n: Optional[int] = None
) -> List[RerankResult]:
    """
    使用带缓存的BM25对文档进行排序
    
    分数说明：
    1. 原始BM25分数：由rank_bm25库计算，理论上可正可负，实际返回 >= 0
    2. 归一化分数：将分数归一化到[0, 1]区间，分数越高表示相关度越高
       - 0分：表示最低相关度
       - 1分：表示最高相关度
    
    Args:
        query_str: 查询字符串
        sections: 待排序的文档列表
        indexed_doc_unique_ids: 文档ID列表，用于缓存查找
        top_n: 返回前n个结果
        
    Returns:
        List[RerankResult]: 排序后的结果列表，每个结果包含：
        - index: 原始索引
        - document: 文档内容
        - relevance_score: 归一化后的相关度分数 [0, 1]
        
    Raises:
        ValueError: 参数验证失败时
    """
    if not query_str:
        raise ValueError("Query string cannot be empty")
    
    if not sections:
        raise ValueError("Documents list cannot be empty")
        
    if indexed_doc_unique_ids and len(sections) != len(indexed_doc_unique_ids):
        raise ValueError("Documents and document IDs must have the same length")
        
    if top_n is not None and top_n <= 0:
        raise ValueError("top_n must be positive")
        
    query_words = jieba_cut_without_stopwords(query_str)
    tokenized_docs = []
    
    # 获取所有文档的TokenizedDoc对象
    for section, doc_id in zip(sections, indexed_doc_unique_ids or [None] * len(sections)):
        tokenized_doc = get_or_create_tokenized_doc_for_section(section, doc_id)
        tokenized_docs.append(tokenized_doc)
    
    # 使用统一接口计算BM25分数
    scores = compute_bm25_scores(query_words, tokenized_docs)
    
    # 创建结果列表
    bm25_results: List[RerankResult] = [
        {
            "index": i,
            "document": section,
            "relevance_score": round(float(score), 5)
        }
        for i, (section, score) in enumerate(zip(sections, scores))
    ]

    # 归一化到[0, 2]区间，与BM25常见分数范围对应
    bm25_results = normalize_scores(bm25_results, 0, 2)
    bm25_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return bm25_results[:top_n] if top_n else bm25_results

if __name__ == "__main__":
    # 测试文档
    test_sections = [
        "人工智能是计算机科学的一个重要分支，主要研究如何让计算机模拟人类智能。",
        "机器学习是人工智能的核心技术之一，通过数据训练来实现智能决策。",
        "深度学习是机器学习的一个分支，使用多层神经网络来学习数据特征。"
    ]
    
    # 模拟文档ID，使用不同的ID以避免缓存混淆
    test_doc_ids = [
        "test_doc_ai_basic",
        "test_doc_machine_learning",
        "test_doc_deep_learning"
    ]
    
    # 测试查询
    test_query = "人工智能机器学习"
    
    print("测试文档:")
    for i, doc in enumerate(test_sections):
        print(f"{i+1}. {doc}")
    print("\n查询语句:", test_query)
    
    # 执行BM25排序
    results = bm25_reorder(
        query_str=test_query,
        sections=test_sections,
        indexed_doc_unique_ids=test_doc_ids
    )
    
    print("\n排序结果:")
    for i, result in enumerate(results):
        print(f"\n第{i+1}名:")
        print(f"文档: {result['document']}")
        print(f"相关度分数: {result['relevance_score']}")