from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from mrag_vdb.dto.rag_input import RagInput

class RagContext(BaseModel):
    """
    用于在RAG处理流程中携带上下文信息的容器类
    保持原始输入不变，同时收集处理过程中的各种中间结果
    """
    # 原始输入(保持不变)
    input: RagInput

    # 查询处理相关
    refined_query: Optional[str] = None  # 查询改写后的结果
    refined_kbnames: Optional[List[str]] = None
    limit_raw: int = 30
    limit_rerank: int = 10

    def get_refined_query(self) -> str:
        if self.refined_query is None:
            return self.input.query
        return self.refined_query
    
    def get_refined_kbnames(self) -> list[str]:
        if self.refined_kbnames is None:
            return self.input.preferred_kbnames
        return []

    def get_limit_raw(self) -> int:
        return self.limit_raw
    
    def get_limit_rerank(self) -> int:
        return self.limit_rerank


if __name__ == "__main__":
    # 使用示例
    from mrag_vdb.dto.rag_input import RagInput
    
    # 创建原始输入
    rag_input = RagInput(
        query="什么是机器学习?",
        user_profile="技术爱好者"
    )
    
    # 创建上下文容器
    context = RagContext(input=rag_input)
    
    # 在处理过程中不断更新信息
    context.refined_query = "解释机器学习的基本概念和应用"
    
    print(context.model_dump_json(indent=2)) 