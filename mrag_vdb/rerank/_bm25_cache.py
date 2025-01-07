from typing import List, Dict, Any, Optional
import msgpack
import os
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv
load_dotenv()

from mrag_vdb.common.vdb_base import get_ref_path

class TokenizedDoc:
    """
    预分词文档的管理类
    
    设计说明：
    1. 只缓存分词结果(tokenized_doc)
       - 分词结果易于序列化和存储
       - 占用空间小
       - 分词是最耗时的步骤，值得缓存
    
    2. 不直接计算BM25分数
       - BM25计算应在文档集合的上下文中进行
       - 遵循rank_bm25库的设计理念
    
    工作流程：
    - 首次处理：文档 -> 分词 -> 存储tokenized_doc
    - 加载缓存：读取tokenized_doc
    """
    __slots__ = ['tokenized_doc']
    
    def __init__(self, tokenized_doc: List[str]) -> None:
        """
        初始化预分词文档对象
        
        Args:
            tokenized_doc: 已分词的文档，词语列表
        """
        self.tokenized_doc = tokenized_doc

    def get_tokenized_doc(self) -> List[str]:
        """获取分词后的文档"""
        return self.tokenized_doc
    
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
    def from_cache(cls, cache_data: Dict[str, Any]) -> 'TokenizedDoc':
        """
        从缓存数据恢复对象
        
        Args:
            cache_data: 包含tokenized_doc的缓存数据
            
        Returns:
            TokenizedDoc: 恢复的对象
            
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

def compute_bm25_scores(query_tokens: List[str], tokenized_docs: List[TokenizedDoc]) -> List[float]:
    """
    计算查询与一组预分词文档的BM25得分
    
    设计说明：
    1. 将所有文档的tokens作为语料库传给BM25Okapi
    2. 确保语料库中至少有一个文档
    3. 使用标准的BM25计算流程
    
    Args:
        query_tokens: 查询文本的分词结果
        tokenized_docs: TokenizedDoc对象列表，每个对象代表一个预分词文档
        
    Returns:
        List[float]: 每个文档对应的BM25得分列表
        
    Example:
        >>> docs = [TokenizedDoc(["文档", "一"]), TokenizedDoc(["文档", "二"])]
        >>> scores = compute_bm25_scores(["查询", "文档"], docs)
    """
    if not tokenized_docs:
        return []
    
    # 收集所有文档的tokens
    corpus = [doc.get_tokenized_doc() for doc in tokenized_docs]
    
    # 初始化BM25计算器
    bm25 = BM25Okapi(corpus)
    
    # 计算得分
    scores = bm25.get_scores(query_tokens)
    
    return [float(score) for score in scores]

if __name__ == "__main__":
    # 简单的测试用例
    def test_tokenized_doc():
        print("测试 TokenizedDoc 基本功能...")
        
        # 测试文档
        docs = [
            TokenizedDoc(["这是", "第一个", "测试", "文档", "关于", "机器学习"]),
            TokenizedDoc(["这是", "第二个", "文档", "关于", "自然语言", "处理"]),
            TokenizedDoc(["第三个", "文档", "讨论", "人工智能", "技术"])
        ]
        
        # 创建实例
        print("\n1. 创建 TokenizedDoc 实例")
        for i, doc in enumerate(docs):
            print(f"文档{i+1}: {' '.join(doc.get_tokenized_doc())}")
        
        # 测试BM25计算（缓存前）
        print("\n2. 缓存前的BM25计算")
        queries = [
            ["机器学习"],
            ["自然语言", "处理"],
            ["人工智能"]
        ]
        
        original_scores = []
        for query in queries:
            scores = compute_bm25_scores(query, docs)
            original_scores.append(scores)
            print(f"\n查询: {' '.join(query)}")
            for i, score in enumerate(scores):
                print(f"文档{i+1}得分: {score:.4f}")
        
        # 测试序列化和反序列化
        print("\n3. 序列化和反序列化所有文档")
        # 序列化和恢复所有文档
        restored_docs = []
        for doc in docs:
            # 序列化
            cache_data = doc.to_cache()
            # 使用msgpack序列化和反序列化
            packed = msgpack.packb(cache_data)
            unpacked = msgpack.unpackb(packed)
            # 从缓存恢复
            restored_doc = TokenizedDoc.from_cache(unpacked)
            restored_docs.append(restored_doc)
        
        # 验证恢复后的BM25计算结果
        print("\n4. 缓存后的BM25计算")
        for query_idx, query in enumerate(queries):
            scores = compute_bm25_scores(query, restored_docs)
            print(f"\n查询: {' '.join(query)}")
            for i, (orig_score, new_score) in enumerate(zip(original_scores[query_idx], scores)):
                print(f"文档{i+1} - 原始得分: {orig_score:.4f}, 恢复后得分: {new_score:.4f}")
                print(f"得分一致: {abs(orig_score - new_score) < 1e-6}")
        
        # 验证文档内容
        print("\n5. 验证文档内容")
        for i, (orig_doc, restored_doc) in enumerate(zip(docs, restored_docs)):
            orig_tokens = orig_doc.get_tokenized_doc()
            restored_tokens = restored_doc.get_tokenized_doc()
            print(f"\n文档{i+1}:")
            print(f"原始tokens: {orig_tokens}")
            print(f"恢复tokens: {restored_tokens}")
            print(f"tokens一致: {orig_tokens == restored_tokens}")
        
        # 测试错误处理
        print("\n6. 测试错误处理")
        try:
            TokenizedDoc.from_cache({})
            print("错误: 应该抛出ValueError")
        except ValueError as e:
            print(f"正确: 捕获到预期的错误 - {e}")
            
        print("\n测试完成!")
    
    # 运行测试
    test_tokenized_doc()
