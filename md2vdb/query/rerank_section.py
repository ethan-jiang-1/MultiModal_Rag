from dotenv import load_dotenv
import sys
import os
#import rich
import jieba
import requests
from rank_bm25 import BM25Okapi

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

def decode_knowlege_from_result(encoded_knowledge):
    decoded_knowledge = encoded_knowledge.replace('[desc]', '')
    decoded_knowledge = decoded_knowledge.replace('---table begin---', 'The following is table:').replace('---table end---', '')
    return decoded_knowledge

def format_result_list(result_list):
    """格式化输出知识段落"""
    string_list = []
    for res in result_list:
        decoded_knowledge = decode_knowlege_from_result(res[3])
        knowledge = "*** New Knowledge Paragraph ***\n" \
                    f"[Source File] {res[2]['filename']} [Source File]\n" \
                    f"[Knowledge Title] {res[2]['title']} [Knowledge Title]\n" \
                    f"[Knowledge Content] {decoded_knowledge} [Knowledge Content]"
        string_list.append(knowledge)
    return string_list

def reset_by_jina(question, results, threshold=0.0, jina_weight=0.8, bm25_weight=0.5):
    # metas每一项是个字典，格式例如：
    # {'filename': 'AN007.csv', 'n_tokens': 304, 'title': '[desc] 如何构建隔离 CAN 方案 __ 集成电源的隔离 CAN 方案 [desc]\r'}
    # 提取输入的各类信息
    url = os.environ["JINA_RERANKER_ENDPOINT"]

    ids = results['ids'][0]
    distances = results['distances'][0]
    metas = results['metadatas'][0]
    documents = results['documents'][0]

    # 归一化 distances 列表
    min_distance = min(distances)
    max_distance = max(distances)
    try:
        normalized_distances = [(distance - min_distance) / (max_distance - min_distance) for distance in distances]
    except ZeroDivisionError:
        normalized_distances = [1.0] * len(ids)  # 如果出现除0情况，直接给所有距离归一化为1

    # 调用Jina服务进行重新排序
    data = {
        'query': question,
        'documents': documents,  # 发送文档列表进行排序
        'count': len(documents),  # 获取所有文档的重新排序结果
    }
    response = requests.post(url, json=data)
    jina_results = response.json()  # 假设返回的是一个按分数排序的元组列表 [(score, document)]

    jina_results_scores = [item[0] for item in jina_results]
    jina_results_documents = [item[1] for item in jina_results]

    # TODO: ignore:Ethan_bm25 only has filename, but not title?
    # 准备文件名和BM25计算
    filenames = [meta['filename'] for meta in metas]  # 提取所有文件名
    tokenized_filenames = [list(jieba.cut(filename)) for filename in filenames]  # 对文件名进行分词
    bm25 = BM25Okapi(tokenized_filenames)  # 构建BM25模型

    # 对查询进行分词
    query_tokens = list(jieba.cut(question))
    bm25_scores = bm25.get_scores(query_tokens)  # 获取BM25分数

    # Jina返回结果已经按分数排序，使用文档重排原始的 ids 和 metas
    result_list = []
    #for jina_score, doc in zip(jina_results['scores'], jina_results['documents']):
    for jina_score, doc in zip(jina_results_scores, jina_results_documents):
        idx = documents.index(doc)  # 找到文档在原始 documents 列表中的索引
        # 基于距离、BM25 和 Jina评分加权
        base_score = 1 - normalized_distances[idx]  # 距离越小，得分越高
        jina_score_weighted = jina_score * jina_weight  # Jina的评分乘以权重
        bm25_score_weighted = bm25_scores[idx] * bm25_weight  # BM25的分数乘以权重
        final_score = base_score + jina_score_weighted + bm25_score_weighted
        result_list.append([ids[idx], final_score, metas[idx], documents[idx]])

    # 按照得分从高到低排序
    result_list = sorted(result_list, key=lambda x: x[1], reverse=True)

    if isinstance(threshold, float) and threshold >= 0.0:
        result_list = [item for item in result_list if item[1] >= threshold]

    # 返回格式化后的结果
    return format_result_list(result_list)
