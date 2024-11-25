import os
import random
import tempfile
import sys
import chromadb
#import tiktoken
import jieba
import pandas as pd
import logging
import rich
from dotenv import load_dotenv

import time
from chromadb.config import Settings # , DEFAULT_TENANT, DEFAULT_DATABASE
from whoosh.index import open_dir
from whoosh.index import create_in
from whoosh.qparser import OrGroup
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

import requests
from rank_bm25 import BM25Okapi

if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from HiQA.utils.filter import filter_product_names, filter_knowledge # , critic_keywords
from HiQA.utils.openai_proxy import get_text_embedding
from HiQA.utils.tokenizer import ChineseAnalyzer, get_token_encoding
from HiQA.utils.util_logging import get_logger_progress, setup_logger_handlers
from HiQA.utils.util_file import get_root_dir

logger_prg = get_logger_progress()

g_settings = Settings(allow_reset=True)

g_ixs = None
g_collections = None

DEFAULT_KLG_MAX_TOKENS = 8000
DEFAULT_KLG_MAX_ITEMS = 5
DEFAULT_KLG_MIN_ITEMS = 3
DEFAULT_FTS_K = 20

def get_knowledge(question, kb_name, max_token=DEFAULT_KLG_MAX_TOKENS, max_item=DEFAULT_KLG_MAX_ITEMS, only_vec=False, verbose=False):
    begin = time.time()
    logger_prg.info("step2.1: 25%: 召回相关知识#嵌入向量准备")
    question_embd = get_text_embedding(question)
    if verbose:
        print('after embedding', time.time() - begin)

    logger_prg.info("step2.2: 30%: 召回相关知识#召回内容片段")
    knowledge = retrieve_knowledge(question, question_embd, kb_name, max_token=max_token, max_item=max_item, only_vec=only_vec, verbose=verbose)
    if verbose:
        print('knowledge length', len(knowledge))
    return knowledge

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

    # TODO Ethan bm25 only has filename, but not title?
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



def reset_by_lucene(question, results, threshold=0.5, lucene_weight=0.5):
    # ids每一项是个字符串，格式例如：'id0'
    # distances每一项是个浮点数，表示embedding的距离
    # metas每一项是个字典，格式例如：
    # {'filename': 'AN007.csv', 'n_tokens': 304, 'title': '[desc] 如何构建隔离 CAN 方案 __ 集成电源的隔离 CAN 方案 [desc]\r'}
    # documents每一项是个字符串，表示文本内容
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
        result_list = []
        for i in range(len(ids)):
            result_list.append(documents[i])
        return result_list

    result_list = []
    for i in range(len(ids)):
        # 只包括那些 distance 值小于 0.5 的项
        # if normalized_distances[i] <= threshold:
            # 1 - distance = 打分
        result_list.append([ids[i], 1 - normalized_distances[i], metas[i], documents[i]])

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            schema = Schema(id=ID(stored=True), content=TEXT(analyzer=ChineseAnalyzer(), stored=True))
            # schema = Schema(id=ID(stored=True), content=TEXT(stored=True))
            idx = create_in(temp_dir, schema)
            writer = idx.writer()

            for res in result_list:
                writer.add_document(id=res[0], content=res[3])
            writer.commit()

            stopwords = {"的", "了", "和", "是", "就", "都", "而", "及", "与"}

            with idx.searcher() as searcher:
                tokens = jieba.cut(question, cut_all=False)
                filtered_tokens = [token for token in tokens if token not in stopwords]
                or_question = " ".join(filtered_tokens)
                parser = QueryParser("content", idx.schema, group=OrGroup)
                query = parser.parse(or_question)
                query_results = searcher.search(query, limit=None)

                scores = [hit.score for hit in query_results]
                max_score = max(scores) if scores else 1
                normalized_scores = [score / max_score for score in scores]
                id_to_score = {hit["id"]: normalized_scores[i] for i, hit in enumerate(query_results)}
    except Exception as e:
        logging.exception(e)
        pass
    for i, res in enumerate(result_list):
        if res[0] in id_to_score:
            result_list[i][1] += id_to_score[res[0]] * lucene_weight

    result_list = sorted(result_list, key=lambda x: x[1], reverse=True)

    string_list = []
    for res in result_list:
        knowledge = "*** New Knowledge Paragraph ***\n" \
                    f"[Source File] {res[2]['filename']} [Source File]\n" \
                    f"[Knowledge Title] {res[2]['title']} [Knowledge Title]\n" \
                    f"[Knowledge Content] {res[3].replace('[desc]', '').replace('---table begin---', 'The following is table:').replace('---table end---', '')} [Knowledge Content]"

        string_list.append(knowledge)

    return string_list


def _do_query_based_on_question_and_dataset(question, collection, question_embd, dataset):
    question = question.upper() # .replace('3741X', '3741').replace('3641X', '3641').replace('3742X', '3741').replace('3642X', '3641')
    # if question.__contains__('经销商') or question.__contains__('销售') or question.__contains__('营销'):
    #     results = collection.query(
    #         query_embeddings=question_embd,
    #         n_results=50,
    #         where_document={"$contains": "经销商"}
    #     )
    # elif dataset == 'Product documents - Chipanalog' and (question.__contains__('竞品') or question.__contains__('替代') or question.__contains__('代替') \
    #         or question.__contains__('竞对') or question.__contains__('竞争') or question.__contains__('对手') \
    #         or question.__contains__('功能一样') or question.__contains__('功能相同') or question.__contains__(
    #     '功能相似') \
    #         or question.__contains__('替换')):
    #     results = enemy_collection.query(
    #         query_embeddings=question_embd,
    #         n_results=50,
    #     )
    # else:
    results = collection.query(
        question_embd,
        n_results=50
    )
    return results

def retrieve_knowledge(question, question_embd, kb_name, max_token=DEFAULT_KLG_MAX_TOKENS, max_item=DEFAULT_KLG_MAX_ITEMS,  only_vec=False, verbose=False):
    global g_init_state
    global g_collections

    if g_collections is None:
        raise ValueError("KC is not inited")

    if kb_name not in g_collections:
        raise ValueError(f"KC {kb_name} not inited")

    begin = time.time()

    collection = g_collections[kb_name]

    results = _do_query_based_on_question_and_dataset(question, collection, question_embd, kb_name)

    if only_vec:
        result_list = [doc for doc in results['documents'][0]]
        string_list = []
        for res in result_list:
            know_chunk_piece = res.replace('[desc]', '').replace('---table begin---', 'The following is table:').replace('---table end---', '')
            knowledge = "*** New Knowledge Paragraph ***\n" \
                        f"[Knowledge Content] {know_chunk_piece} [Knowledge Content]"

            string_list.append(knowledge)

        # early return to avoid lucene and keyword
        return '\n\n'.join(string_list)

    if verbose:
        logging.info(f'ck1: after retrieve {time.time() - begin}')
    
    logger_prg.info("step2.3: 35%: 召回相关知识#按内容相关性重排序")
    # result_list = reset_by_lucene(question, results, threshold=0.5, lucene_weight=0.5)
    result_list = reset_by_jina(question, results, threshold=0.0)

    if isinstance(max_item, int) and max_item > DEFAULT_KLG_MIN_ITEMS:
        result_list = result_list[:max_item]
    
    if verbose:
        logging.info(f'ck2: after rank by reset_by_jina {time.time() - begin}')

    logger_prg.info("step2.4: 40%: 召回相关知识#过滤知识片段")
    returned_values = filter_knowledge(question, result_list)

    if verbose:
        logging.info(f'ck3: after filter: {time.time() - begin}')

    all_text = returned_values

    tk_encoding = get_token_encoding()
    # reduce length to max_token
    tokens = tk_encoding.encode(all_text)
    truncated_text = all_text

    max_token = int(max_token)
    while len(tokens) > max_token:
        truncated_text = truncated_text[:-200]
        tokens = tk_encoding.encode(truncated_text)
    if verbose:
        logging.info(f'ck4: after truncate : {time.time() - begin}')
    return truncated_text


def has_key_words(item, product_in_query):
    name = item[0]
    content = item[1]
    for product in product_in_query:
        if product in name or product in content:
            return True
    return False


def _get_images_foldernames_as_products(kb_name):
    dir_root = get_root_dir()
    dir_images = os.path.join(dir_root,f'datasets/{kb_name}/images')
    if not os.path.isdir(dir_images):
        return []

    # 获取目录下的所有文件和子目录名
    entries = os.listdir(dir_images)

    # 过滤出子目录，并对其进行排序
    subdirectories = sorted([d for d in entries if os.path.isdir(os.path.join(dir_images, d))])
    return subdirectories

def _find_suitable_querys_for_image(user_input, response, kb_name, lang='CN'):
    default_products = _get_images_foldernames_as_products(kb_name)
    product_in_query = filter_product_names(user_input, default_products)
    product_in_response = filter_product_names(response, default_products)
    # print('product_in_query', product_in_query)
    # print('product_in_response', product_in_response)
    if not product_in_query and not product_in_response:
        query = user_input + ' ' + response[:min(300, len(response))]
    if product_in_response:
        query = user_input + ' ' + response
    if product_in_query:
        query = user_input

    query = user_input
    # Tokenize the query string and join tokens with OR operator
    if lang == 'CN':
        query_tokens = jieba.cut(query, cut_all=True)
    else:
        query_tokens = query.split()
    return query_tokens, product_in_query,  product_in_response

def _keep_matched_suitable_image_descs(results_fts, source_match_name, image_path_base):
    results_list = [(hit['file_name'], hit['content'], hit.score) for hit in results_fts]
    # keywords_result = [item for item in results_list if item[2] > 10 and has_key_words(item, product_in_query)]
    # if len(keywords_result) > 0:
    #     results_list = keywords_result

    image_descs = []
    for result in results_list:
        # print('content:', result[1])
        image_name = result[0]  # name
        base_name = image_name.split('_img')[0] # _imgbmp or _imgsvg ,  see load_imgs_from_pdf

        if source_match_name.find(base_name) == -1:
            continue

        image_full_path = os.path.join(image_path_base, 'images', base_name, image_name + '.png')
        image_full_path = os.path.abspath(image_full_path)

        try:
            image_title = result[1].split('\n')[0].split(':')[1]  # line3desc
        except IndexError:
            try:
                image_title = result[1].split('\n')[0].split(':')[0]
            except IndexError:
                image_title = 'Title not found'

        image_title = _remove_repeated_substrings(image_title)
        #                    0:full_path      1:title      2:score   3:img_name  4:content
        image_descs.append((image_full_path, image_title, result[2], image_name, result[1]))
    return image_descs

def _rerank_image_descs(images_descs, product_in_query, product_in_response):
    # do filter image, re-rank all images, appear in query first, then reamin
    images_descs_reranked = []
    images_remain = []
    for image in images_descs:
        print('title:', image[1])
        print('name:', image[3])
        print('content:', image[4])
        img_desc = image[1] + ' ' + image[3] + ' ' + image[4]
        add = False
        for product in product_in_query:
            if product in img_desc:
                images_descs_reranked.append(image)
                add = True
                break
        if not add:
            images_remain.append(image)

    print('after input filter:', len(images_descs_reranked))
    print('after input filter remain: ', len(images_remain))

    images_rrmain = []
    for image in images_remain:
        img_desc = image[1] + ' ' + image[3] + ' ' + image[4]
        add = False
        for product in product_in_response:
            if product in img_desc:
                images_descs_reranked.append(image)
                add = True
                break
        if not add:
            images_rrmain.append(image)
    
    print('after output filter:', len(images_descs_reranked))
    print('after input filter remain: ', len(images_rrmain))

    images_descs_reranked.extend(images_rrmain)
    print('final return: ', len(images_descs_reranked))
    return images_descs_reranked



def search_images_from_response(user_input, response, kb_name, source_match,
                                lang='CN', 
                                k=DEFAULT_FTS_K):
    global g_ixs
    if not isinstance(source_match, str) or len(source_match) == 0:
        return []

    dir_root = get_root_dir()
    directory = os.path.join(dir_root,f'datasets/{kb_name}/')
    if not os.path.isdir(directory):
        raise ValueError(f"dataset: {directory} not exist")

    image_path_base = os.path.join(dir_root, f"datasets/{kb_name}")

    source_match_name = os.path.basename(source_match)  # source_match is citation name 

    query_tokens, product_in_query,  product_in_response = _find_suitable_querys_for_image(user_input, response, kb_name, lang=lang)

    ix = g_ixs[kb_name] # whoosh is a FTS local engine 
    or_query = " OR ".join(query_tokens)
    parser = QueryParser("content", ix.schema)
    query_whoosh = parser.parse(or_query)

    with ix.searcher() as searcher:
        results_fts = searcher.search(query_whoosh, limit=k)

        image_descs = _keep_matched_suitable_image_descs(results_fts, source_match_name, image_path_base)

        images_descs_reranked = _rerank_image_descs(image_descs, product_in_query, product_in_response)

        return images_descs_reranked
        # return images


def _remove_repeated_substrings(s):
    def longest_repeated_substring(text):
        n = len(text)
        table = [[0] * n for _ in range(n)]
        longest_substring = ''
        longest_length = 0

        for i in range(n):
            for j in range(i + 1, n):
                if text[i] == text[j]:
                    if i == 0 or j == 0:
                        table[i][j] = 1
                    else:
                        table[i][j] = table[i - 1][j - 1] + 1

                    if table[i][j] > longest_length:
                        longest_substring = text[i - table[i][j] + 1: i + 1]
                        longest_length = table[i][j]
                else:
                    table[i][j] = 0

        return longest_substring

    longest_substring = longest_repeated_substring(s)
    while len(longest_substring) > 2:
        s = s.replace(longest_substring, '', 1)
        longest_substring = longest_repeated_substring(s)

    return s


def create_and_load_collection(chromadb_client, base_name, dataset_path):
    # 生成唯一的集合名称
    collection_name = base_name+ str(random.randint(0, 10000))

    # 创建集合
    collection = chromadb_client.create_collection(name=collection_name)
    logging.info(f'CALC: Collection {collection_name} created')

    # 加载数据
    embds = []
    docs = []
    metas = []
    ids = []
    id = 0

    for filename in os.listdir(dataset_path):
        if filename.endswith('.csv'):
            filepath = os.path.join(dataset_path, filename)
            if os.path.getsize(filepath) <= 2:
                logging.warning(f"{filepath} is empty")
                continue
            try:
                df = pd.read_csv(filepath)
                for _, row in df.iterrows():
                    section = row['section']
                    n_tokens = row['n_tokens']
                    embedding = [float(value) for value in row['embedding'][1:-1].split(',')]
                    embds.append(embedding)
                    docs.append(section)
                    ids.append('id' + str(id))

                    metas.append({'n_tokens': n_tokens, 'filename': filename, 'title': section.split('\n')[0]})
                    id += 1
            except Exception as ex:
                logging.exception(f"{ex} @{filepath}")

    logging.info(f'CALC: Collection {collection_name} filled into chromadb from scratch (load from csv)')
    logging.info(f"CALC: num_embedding: {len(embds)} num_docs: {len(docs)} num_metas: {len(metas)} ids: {len(ids)}")
    collection.add(embeddings=embds, documents=docs, metadatas=metas, ids=ids)
    return collection


def init_kc(kb_name):
    global g_ixs
    global g_collections
    global g_settings
    #global enemy_collection

    if g_collections is not None and kb_name in g_collections:
        return True

    try:
        setup_logger_handlers()
        logging.info(f'IKC: init project, kb_name:{kb_name}...')

        'or'.join(jieba.cut("pre load"))
        logging.info(f"'IKC: load jieba")

        dir_root = get_root_dir()

        # load whoosh dictionary for image search
        ix_test = open_dir(os.path.join(dir_root, f'datasets/{kb_name}/indexes'))
        g_ixs = {}
        g_ixs[kb_name] = ix_test
        logging.info(f"'IKC: load whoosh index for images")

        rich.print(g_settings)
        chroma_client = chromadb.Client(settings=g_settings)
        chroma_client.reset()
        logging.info("'IKC: load chromadb for text")

        g_collections = {}
        g_collections[kb_name] = create_and_load_collection(chroma_client, kb_name, os.path.join(dir_root, f'datasets/{kb_name}/embeddings'))
        logging.info(f'IKC: load kb_name:{kb_name} successful')

        return True

    except Exception as ex:
        logging.exception(ex)
        return False

if __name__ == "__main__":
    #kb_name = "text"
    kb_name = "exam"
    init_kc(kb_name)

