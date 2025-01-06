#import logging
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.rerank._base_rerank import RerankResult, normalize_scores 
from mrag_vdb.rerank._bm25_cache_section import get_or_create_bm25_for_section

def bm25_reorder(
    query_str: str, 
    sections: List[str], 
    indexed_doc_unique_ids: Optional[List[str]] = None, 
    top_n: Optional[int] = None
) -> List[RerankResult]:
    """
    使用带缓存的BM25对文档进行排序
    
    Args:
        query_str: 查询字符串
        documents: 待排序的文档列表
        indexed_doc_unique_ids: 文档ID列表，用于缓存查找
        top_n: 返回前n个结果
        
    Returns:
        List[BM25Result]: 排序后的结果列表
        
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
    bm25_results: List[RerankResult] = []

    for i, (section, doc_id) in enumerate(zip(sections, indexed_doc_unique_ids or [None] * len(sections))):
        cached_bm25 = get_or_create_bm25_for_section(section, doc_id)
        score = cached_bm25.get_scores(query_words)[0]
        
        bm25_results.append({
            "index": i,
            "document": section,
            "relevance_score": round(float(score), 5)
        })

    bm25_results = normalize_scores(bm25_results, -20, 20)
    bm25_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return bm25_results[:top_n] if top_n else bm25_results

if __name__ == "__main__":
    # 测试文档
    test_sections = [
        "人工智能是计算机科学的一个重要分支，主要研究如何让计算机模拟人类智能。",
        "机器学习是人工智能的核心技术之一，通过数据训练来实现智能决策。",
        "深度学习是机器学习的一个分支，使用多层神经网络来学习数据特征。"
    ]
    
    # 模拟文档ID
    test_doc_ids = [
        "mrag_1__座椅STO间隙_P1_28b5d804",
        "mrag_1__座椅STO间隙_P1_28b5d804",
        "mrag_1__座椅STO间隙_P1_28b5d804"
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