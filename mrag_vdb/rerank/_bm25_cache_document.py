import logging
import os
import msgpack  # 需要先 pip install msgpack
import json
import shutil
import numpy as np

from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
from mrag_vdb.common.vdb_base import get_ref_path
from mrag_vdb.rerank._bm25_cache import TokenizedDoc, get_cached_bm25_folder, compute_bm25_scores
from mrag_vdb.utils.util_logging import setup_logger_handlers


def get_bm25_cache_path_for_document(doc_unique_id: str) -> Optional[str]:
    """
    生成缓存文件路径
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        Optional[str]: 缓存文件路径，如果无法创建则返回None
    """
    doc_folder = get_cached_bm25_folder(doc_unique_id)
    if doc_folder is not None:
        return os.path.join(doc_folder, f"bm25_content.msgpack")  # 使用.msgpack后缀
    return None


def get_or_create_tokenized_doc_for_document(doc_unique_id: str) -> TokenizedDoc:
    """
    基于文档元信息创建预分词文档对象
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        TokenizedDoc: 预分词文档对象
        
    Raises:
        IOError: 文件读写失败时
        ValueError: 元信息格式不正确时
    """
    # 先检查是否有缓存
    cache_path = get_bm25_cache_path_for_document(doc_unique_id)
    if cache_path is not None:
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = msgpack.unpack(f)
                logging.info(f"Loaded cached TokenizedDoc for document {doc_unique_id}")
                return TokenizedDoc.from_cache(cache_data)
            except Exception as e:
                logging.warning(f"Failed to load cached TokenizedDoc for document {doc_unique_id}: {e}")
    
    # 读取文档元信息
    ref_path = get_ref_path()
    meta_path = os.path.join(ref_path, doc_unique_id, "doc_meta.json")
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            doc_meta = json.load(f)
        
        if 'doc_summary' not in doc_meta:
            raise ValueError(f"No doc_summary found in meta file for document {doc_unique_id}")
            
        # 使用doc_summary创建TokenizedDoc对象
        tokenized_doc = jieba_cut_without_stopwords(doc_meta['doc_summary'])
        tokenized_doc_obj = TokenizedDoc(tokenized_doc)
        
        # 保存到缓存
        if cache_path:
            try:
                with open(cache_path, 'wb') as f:
                    msgpack.pack(tokenized_doc_obj.to_cache(), f)
                logging.info(f"Cached TokenizedDoc for document {doc_unique_id}")
            except Exception as e:
                logging.warning(f"Failed to cache TokenizedDoc for document {doc_unique_id}: {e}")
        
        return tokenized_doc_obj
        
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Failed to read meta file for document {doc_unique_id}: {e}")
        raise


if __name__ == "__main__":
    setup_logger_handlers()
    
    # 创建测试文档
    test_doc_id = "test_doc_12345678"
    ref_path = get_ref_path()
    test_doc_dir = os.path.join(ref_path, test_doc_id)
    os.makedirs(test_doc_dir, exist_ok=True)
    
    # 创建测试用的doc_meta.json
    test_meta = {
        "doc_summary": """
        机器学习 机器学习 机器学习 机器学习 机器学习 机器学习 机器学习 机器学习 机器学习 机器学习
        算法 算法 算法 算法 算法 算法 算法 算法 算法 算法
        深度学习 深度学习 深度学习 深度学习 深度学习
        这是一个专门用来测试BM25评分的文档。
        文档中极端高频出现某些词语是为了测试词频惩罚机制。
        神经网络 神经网络 神经网络 神经网络 神经网络。
        """,
        "title": "BM25评分测试"
    }
    
    try:
        # 写入测试元数据
        meta_path = os.path.join(test_doc_dir, "doc_meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(test_meta, f, ensure_ascii=False, indent=2)
        
        # 测试场景1：首次创建TokenizedDoc
        print("\n1. 首次创建TokenizedDoc")
        doc = get_or_create_tokenized_doc_for_document(test_doc_id)
        print(f"分词结果: {' '.join(doc.get_tokenized_doc())}")
        
        # 测试场景2：从缓存加载
        print("\n2. 从缓存加载TokenizedDoc")
        cached_doc = get_or_create_tokenized_doc_for_document(test_doc_id)
        print("验证分词结果一致:", doc.get_tokenized_doc() == cached_doc.get_tokenized_doc())
        
        # 测试场景3：计算BM25得分
        print("\n3. 测试BM25计算")
        
        # 创建三个测试文档，用于对比不同情况下的分数
        docs = [
            doc,  # 文档1：原始文档（高频词：机器学习、算法、深度学习、神经网络）
            TokenizedDoc(jieba_cut_without_stopwords("""
            机器学习是重要技术。算法很关键。
            这个文档包含相关词但频率正常。
            深度学习和神经网络都只出现一次。
            """)),  # 文档2：相关词出现但频率正常
            TokenizedDoc(jieba_cut_without_stopwords("""
            这是一个完全不相关的文档。
            用来测试文档相关性打分。
            数据库 数据库 数据库 网络 网络。
            """)),  # 文档3：不相关文档（高频词：数据库、网络）
        ]
        
        print("\n测试用例A：查询词在文档中出现且频率不同")
        query_a = ["机器学习", "算法"]
        scores_a = compute_bm25_scores(query_a, docs)
        print(f"查询: '{' '.join(query_a)}'")
        print(f"文档1（高频）得分: {scores_a[0]:.4f}")
        print(f"文档2（低频）得分: {scores_a[1]:.4f}")
        print(f"文档3（无关）得分: {scores_a[2]:.4f}")
        
        print("\n测试用例B：查询词在某些文档中完全不出现")
        query_b = ["数据库", "网络"]
        scores_b = compute_bm25_scores(query_b, docs)
        print(f"查询: '{' '.join(query_b)}'")
        print(f"文档1（无此词）得分: {scores_b[0]:.4f}")
        print(f"文档2（无此词）得分: {scores_b[1]:.4f}")
        print(f"文档3（高频）得分: {scores_b[2]:.4f}")
        
        print("\n测试用例C：混合查询（一个词出现，一个词不出现）")
        query_c = ["机器学习", "数据库"]
        scores_c = compute_bm25_scores(query_c, docs)
        print(f"查询: '{' '.join(query_c)}'")
        print(f"文档1（部分匹配高频）得分: {scores_c[0]:.4f}")
        print(f"文档2（部分匹配低频）得分: {scores_c[1]:.4f}")
        print(f"文档3（部分匹配高频）得分: {scores_c[2]:.4f}")
        
        print("\n测试用例D：词频饱和度测试")
        docs_freq = [
            TokenizedDoc(jieba_cut_without_stopwords("测试词 测试词")),  # 出现2次
            TokenizedDoc(jieba_cut_without_stopwords("测试词 测试词 测试词 测试词 测试词")),  # 出现5次
            TokenizedDoc(jieba_cut_without_stopwords("测试词 "*20))  # 出现20次
        ]
        query_d = ["测试词"]
        scores_d = compute_bm25_scores(query_d, docs_freq)
        print(f"查询: '{' '.join(query_d)}'")
        print(f"文档1（词频=2）得分: {scores_d[0]:.4f}")
        print(f"文档2（词频=5）得分: {scores_d[1]:.4f}")
        print(f"文档3（词频=20）得分: {scores_d[2]:.4f}")
        
        print("\n测试用例E：极端词频对比测试")
        # 创建三个极端情况的文档
        docs_extreme = [
            # 文档1：一个词出现100次，另一个词出现1次
            TokenizedDoc(jieba_cut_without_stopwords("测试词A "*100 + " 测试词B")),
            # 文档2：两个词都出现2次
            TokenizedDoc(jieba_cut_without_stopwords("测试词A 测试词A 测试词B 测试词B")),
            # 文档3：一个词出现1次，另一个词出现100次
            TokenizedDoc(jieba_cut_without_stopwords("测试词A " + "测试词B "*100))
        ]
        
        # 测试不同的查询组合
        queries = [
            ["测试词A"],  # 单词查询
            ["测试词B"],  # 单词查询
            ["测试词A", "测试词B"]  # 多词查询
        ]
        
        for query in queries:
            scores = compute_bm25_scores(query, docs_extreme)
            print(f"\n查询: '{' '.join(query)}'")
            print(f"文档1（A:100次, B:1次）得分: {scores[0]:.4f}")
            print(f"文档2（A:2次, B:2次）得分: {scores[1]:.4f}")
            print(f"文档3（A:1次, B:100次）得分: {scores[2]:.4f}")
        
        print("\n极端词频分析：")
        print("- 当文档中某个词的频率极高时，BM25会给予惩罚")
        print("- 词频的不平衡可能导致负分，特别是在多词查询时")
        print("- 相比之下，词频平衡的文档往往得分更高")
        
        print("\n分数解释：")
        print("- 正分：表示文档与查询相关，分数越高相关性越强")
        print("- 零分：表示查询词在文档中完全未出现")
        print("- 负分：可能出现在词频不均衡的情况下，BM25对高频词的惩罚机制导致")
        
        print("\n测试用例F：手动BM25计算（展示负分情况）")
        
        def simple_bm25_score(tf, df, doc_len, avgdl, N, k1=1.5, b=0.75):
            """简化版的BM25计算，不做任何分数限制"""
            idf = np.log((N - df + 0.5) / (df + 0.5))
            tf_part = tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avgdl))
            return idf * tf_part
        
        # 模拟极端情况
        N = 3  # 文档总数
        avgdl = 50  # 平均文档长度
        
        # 情况1：词频极高，文档很长
        tf1, df1 = 1000, 1  # 词出现1000次，但只在1个文档中
        doc_len1 = 1200  # 文档长度远超平均
        score1 = simple_bm25_score(tf1, df1, doc_len1, avgdl, N)
        
        # 情况2：词频适中，文档长度正常
        tf2, df2 = 5, 2  # 词出现5次，在2个文档中
        doc_len2 = 45  # 文档长度接近平均
        score2 = simple_bm25_score(tf2, df2, doc_len2, avgdl, N)
        
        # 情况3：词频低，文档很短
        tf3, df3 = 1, 3  # 词出现1次，在所有文档中都有
        doc_len3 = 10  # 文档很短
        score3 = simple_bm25_score(tf3, df3, doc_len3, avgdl, N)
        
        print("\n原始BM25公式计算结果（未经过分数限制）：")
        print(f"情况1（极端词频）得分: {score1:.4f}")
        print(f"情况2（正常情况）得分: {score2:.4f}")
        print(f"情况3（常见词）得分: {score3:.4f}")
        
        print("\nBM25分数分析：")
        print("1. 负分出现的原因：")
        print("   - IDF项可能为负数（当词在大多数文档中出现时）")
        print("   - 极端词频和文档长度的组合也可能导致负分")
        print("2. rank_bm25库可能对这些负分进行了处理，将其转换为0")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_doc_dir):
            shutil.rmtree(test_doc_dir)