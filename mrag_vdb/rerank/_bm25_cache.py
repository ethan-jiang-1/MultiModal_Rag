from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import msgpack
#import os

class CachedBM25:
    """
    BM25计算结果的缓存封装类
    """
    __slots__ = ['bm25', 'tokenized_doc']
    
    def __init__(self, tokenized_doc: List[str]) -> None:
        self.bm25 = BM25Okapi([tokenized_doc])
        self.tokenized_doc = tokenized_doc
    
    def get_scores(self, query_terms: List[str]) -> List[float]:
        return self.bm25.get_scores(query_terms)
    
    def to_cache(self) -> Dict[str, Any]:
        return {
            'tokenized_doc': self.tokenized_doc,
            'version': '1.0'
        }
    
    @classmethod
    def from_cache(cls, cache_data: Dict[str, Any]) -> 'CachedBM25':
        if 'tokenized_doc' not in cache_data:
            raise ValueError("Invalid cache data: missing tokenized_doc")
        return cls(cache_data['tokenized_doc'])

if __name__ == "__main__":
    # 简单的测试用例
    def test_cached_bm25():
        print("测试 CachedBM25 基本功能...")
        
        # 测试文档和查询
        doc = ["这是", "一个", "测试", "文档"]
        query = ["测试", "文档"]
        
        # 创建实例
        print("\n1. 创建 CachedBM25 实例")
        bm25 = CachedBM25(doc)
        score = bm25.get_scores(query)[0]
        print(f"文档: {' '.join(doc)}")
        print(f"查询: {' '.join(query)}")
        print(f"BM25分数: {score:.4f}")
        
        # 测试序列化
        print("\n2. 测试序列化和反序列化")
        # 序列化
        cache_data = bm25.to_cache()
        print(f"序列化数据: {cache_data}")
        
        # 使用msgpack序列化和反序列化
        packed = msgpack.packb(cache_data)
        unpacked = msgpack.unpackb(packed)
        
        # 从缓存恢复
        restored_bm25 = CachedBM25.from_cache(unpacked)
        restored_score = restored_bm25.get_scores(query)[0]
        
        print(f"原始分数: {score:.4f}")
        print(f"恢复后分数: {restored_score:.4f}")
        print(f"分数一致: {abs(score - restored_score) < 1e-6}")
        
        # 测试错误处理
        print("\n3. 测试错误处理")
        try:
            CachedBM25.from_cache({})
            print("错误: 应该抛出ValueError")
        except ValueError as e:
            print(f"正确: 捕获到预期的错误 - {e}")
            
        print("\n测试完成!")
    
    # 运行测试
    test_cached_bm25()
