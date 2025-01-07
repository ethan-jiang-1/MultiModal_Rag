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
    
    BM25评分特点说明：
    1. 分数区间：
       - 理论上，原始BM25分数可以是正数或负数
       - rank_bm25库实际返回的分数 >= 0（可能将负分转换为0）
       - 实践中常见分数范围：0 ~ 2.0，极端情况可能更高
    
    2. 分数含义：
       - 0分：查询词在文档中完全未出现
       - 低分（0~0.5）：查询词出现但相关性较弱
       - 中等分数（0.5~1.0）：查询词出现且有一定相关性
       - 高分（>1.0）：查询词出现且相关性强
    
    3. 影响因素：
       a) IDF（逆文档频率）：
          - 词在越少的文档中出现，IDF越高
          - 词在所有文档中都出现，IDF可能为负
          - IDF = log((N-df+0.5)/(df+0.5))，N为文档总数，df为词出现的文档数
       
       b) TF（词频）：
          - 词在文档中出现次数越多，分数越高，但增长不是线性的
          - 有饱和效应：词频很高时分数增长会变缓
          - 极端高频会受到惩罚
       
       c) 文档长度：
          - 通过参数b(0.75)进行长度归一化
          - 过长文档会被适当降低分数
    
    4. 多词查询：
       - 最终分数是各个查询词得分的总和
       - 词频不平衡可能导致某些词贡献负分
       - rank_bm25库可能将负分截断为0
    
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
