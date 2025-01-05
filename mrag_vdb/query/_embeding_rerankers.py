from typing import List
from dotenv import load_dotenv
import os
import dashscope
import logging
import rich
import httpx
import time

# 加载环境变量
load_dotenv()

from mrag_vdb.query._rerank_base import RerankResult, normalize_scores

MAX_DOC_LEN = 3000  # max len restricted by RERANK

    
def qwen_gte_rerank(query_str:str, documents: List[str], top_n: int = None) -> List[RerankResult]:
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

def autodl_jina_rerank(query_str:str, documents: List[str], top_n: int = None) -> List[RerankResult]:
    url = os.getenv("JINA_RERANKER_ENDPOINT")

    documents = [item[:MAX_DOC_LEN] for item in documents]

    # 调用Jina服务进行重新排序
    data = {
        'query': query_str,
        'documents': documents,  # 发送文档列表进行排序
        'count': len(documents),  # 获取所有文档的重新排序结果
    }
    
    max_retries = 3
    with httpx.Client() as client:
        for attempt in range(max_retries):
            try:
                response = client.post(url, json=data, timeout=10.0)
                response.raise_for_status()
                jina_results = response.json()
                
                rerank_results = []
                for i, results_item in enumerate(jina_results):
                    rerank_results.append({
                        "index": i,
                        "document": results_item[1],
                        "relevance_score": round(float(results_item[0]), 5)
                    })
                rerank_results = normalize_scores(rerank_results, -3, 1)
                return rerank_results
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the last exception if all retries failed
                
                delay = (attempt + 1) * 1
                logging.warning(f"Request attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
                time.sleep(delay)

def jinaai_jina_rerank(query_str:str, documents: List[str], top_n: int = None) -> List[RerankResult]:
    documents = [item[:MAX_DOC_LEN] for item in documents]

    url = 'https://api.jina.ai/v1/rerank'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("JINA_API_KEY")}'
    }
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query_str,
        "top_n": None,
        "documents": documents
    }

    max_retries = 3
    with httpx.Client() as client:
        for attempt in range(max_retries):
            try:
                response = client.post(url, headers=headers, json=data, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                rerank_results = []
                results = data["results"]
                for i, results_item in enumerate(results):
                    rerank_results.append({
                        "index": i,
                        "document": results_item["document"]["text"],
                        "relevance_score": round(float(results_item["relevance_score"]), 5)
                    })
                rerank_results = normalize_scores(rerank_results, 0, 1)
                return rerank_results
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise  # Re-raise the last exception if all retries failed
                
                delay = (attempt + 1) * 1
                logging.warning(f"Request attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
                time.sleep(delay)

if __name__ == "__main__":
    from mrag_vdb.utils.util_logging import setup_logger_handlers

    setup_logger_handlers()

    query_str = "hello"
    documents = ["hello", "你好", "hi", "hey", "nihao", "sh", "bad", "silly"]

    ret = qwen_gte_rerank(query_str, documents, top_n=None)
    rich.print("qwen_gte_rerank",ret)

    ret = autodl_jina_rerank(query_str, documents, top_n=None)
    rich.print("autodl_jina_rerank", ret)

    ret = jinaai_jina_rerank(query_str, documents, top_n=None)
    rich.print("jinaai_jina_rerank",ret)