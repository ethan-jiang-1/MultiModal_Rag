from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import msgpack
import os
from dotenv import load_dotenv
load_dotenv()

from mrag_vdb.common.vdb_base import get_ref_path

class TokenizedDocBM25:
    """
    基于预分词文档的BM25实现
    
    设计说明：
    1. 只缓存分词结果(tokenized_doc)，而不是完整的BM25计算结果
       - 分词结果易于序列化和存储
       - 占用空间小
       - 分词是最耗时的步骤，值得缓存
    
    2. 每次加载时重新初始化BM25Okapi
       - BM25的初始化和计算速度较快
       - 避免存储和序列化复杂的BM25对象
    
    工作流程：
    - 首次处理：文档 -> 分词 -> 存储tokenized_doc
    - 加载缓存：读取tokenized_doc -> 初始化BM25 -> 计算相关度
    """
    __slots__ = ['bm25', 'tokenized_doc']
    
    def __init__(self, tokenized_doc: List[str]) -> None:
        """
        初始化BM25缓存对象
        
        Args:
            tokenized_doc: 已分词的文档，词语列表
        """
        self.bm25 = BM25Okapi([tokenized_doc])  # 每次都重新初始化BM25
        self.tokenized_doc = tokenized_doc

    def get_tokenized_doc(self) -> List[str]:
        return self.tokenized_doc
    
    def get_score(self, query: str) -> float:
        """
        计算查询与文档的BM25得分
        
        Args:
            query: 查询文本
            
        Returns:
            float: BM25相关度得分
        """
        from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
        query_tokens = jieba_cut_without_stopwords(query)
        scores = self.bm25.get_scores(query_tokens)
        return float(scores[0])  # 返回第一个（也是唯一的）文档的得分
    
    def get_scores(self, queries: List[str]) -> List[float]:
        """
        批量计算多个查询与文档的BM25得分
        
        Args:
            queries: 查询文本列表
            
        Returns:
            List[float]: BM25相关度得分列表
        """
        from mrag_vdb.rerank._bm25_jieba_cutter import jieba_cut_without_stopwords
        scores = []
        # 逐个处理每个查询
        for query in queries:
            query_tokens = jieba_cut_without_stopwords(query)
            score = self.bm25.get_scores(query_tokens)[0]  # 获取唯一文档的得分
            scores.append(float(score))
        return scores
    
    def to_cache(self) -> Dict[str, Any]:
        """
        序列化为可缓存的格式
        只保存分词结果和版本信息
        """
        return {
            'tokenized_doc': self.tokenized_doc,
            'version': '1.0'
        }
    
    @classmethod
    def from_cache(cls, cache_data: Dict[str, Any]) -> 'TokenizedDocBM25':
        """
        从缓存数据恢复BM25对象
        
        Args:
            cache_data: 包含tokenized_doc的缓存数据
            
        Returns:
            TokenizedDocBM25: 重新初始化的BM25对象
            
        Raises:
            ValueError: 缓存数据格式无效
        """
        if 'tokenized_doc' not in cache_data:
            raise ValueError("Invalid cache data: missing tokenized_doc")
        return cls(cache_data['tokenized_doc'])
    
def get_cached_bm25_folder(doc_unique_id: str) -> Optional[str]:
    """
    获取BM25缓存文件夹路径
    
    Args:
        doc_unique_id: 文档唯一标识符
        
    Returns:
        Optional[str]: 缓存文件夹路径，如果创建失败则返回None
    """
    ref_path = get_ref_path()
    doc_ref_dir = os.path.join(ref_path, doc_unique_id)
    if os.path.isdir(doc_ref_dir):
        cached_bm25_folder = os.path.join(doc_ref_dir, "cached_bm25")
        os.makedirs(cached_bm25_folder, exist_ok=True)
        if os.path.isdir(cached_bm25_folder):
            return cached_bm25_folder
    return None


if __name__ == "__main__":
    # 简单的测试用例
    def test_tokenized_doc_bm25():
        print("测试 TokenizedDocBM25 基本功能...")
        
        # 测试文档和查询
        doc = ["这是", "一个", "测试", "文档", "关于", "机器学习", "和", "人工智能"]
        queries = ["机器学习", "自然语言处理", "人工智能"]
        
        # 创建实例
        print("\n1. 创建 TokenizedDocBM25 实例")
        tdbm25 = TokenizedDocBM25(doc)
        print(f"文档: {' '.join(doc)}")
        
        # 测试单个查询
        print("\n2. 测试 get_score 方法")
        for query in queries:
            score = tdbm25.get_score(query)
            print(f"查询: '{query}' 的BM25得分: {score:.4f}")
        
        # 测试批量查询
        print("\n3. 测试 get_scores 方法")
        scores = tdbm25.get_scores(queries)
        for query, score in zip(queries, scores):
            print(f"查询: '{query}' 的BM25得分: {score:.4f}")
        
        # 测试序列化和反序列化
        print("\n4. 测试序列化和反序列化")
        # 序列化
        cache_data = tdbm25.to_cache()
        print(f"序列化数据: {cache_data}")
        # 使用msgpack序列化和反序列化
        packed = msgpack.packb(cache_data)
        unpacked = msgpack.unpackb(packed)
        
        # 从缓存恢复
        restored_bm25 = TokenizedDocBM25.from_cache(unpacked)
        
        # 验证恢复后的结果
        print("\n5. 验证缓存恢复结果")
        original_scores = tdbm25.get_scores(queries)
        restored_scores = restored_bm25.get_scores(queries)
        
        print("原始得分 vs 恢复后得分:")
        for query, orig_score, rest_score in zip(queries, original_scores, restored_scores):
            print(f"查询: '{query}'")
            print(f"  原始得分: {orig_score:.4f}")
            print(f"  恢复得分: {rest_score:.4f}")
            print(f"  得分一致: {abs(orig_score - rest_score) < 1e-6}")
        
        # 测试错误处理
        print("\n6. 测试错误处理")
        try:
            TokenizedDocBM25.from_cache({})
            print("错误: 应该抛出ValueError")
        except ValueError as e:
            print(f"正确: 捕获到预期的错误 - {e}")
            
        print("\n测试完成!")
    
    # 运行测试
    test_tokenized_doc_bm25()
