from pydantic import BaseModel
from typing import List, Optional, TypedDict
import rich

class Conversation(TypedDict):
    role: str 
    text: str 

class RagInput(BaseModel):
    query: str
    user_profile: Optional[str] = None
    conversation_history: Optional[List[Conversation]] = None
    preferred_kbnames: Optional[List[str]] = None

if __name__ == "__main__":
    # 示例1: 包含所有字段
    example1 = RagInput(
        query="什么是机器学习?",
        user_profile="技术爱好者",
        conversation_history=[
            {"role": "user", "text": "你好"},
            {"role": "assistant", "text": "你好!我能帮你什么?"},
        ],
        preferred_kbnames=["ml_kb", "ai_kb"]
    )
    rich.print("示例1:", example1.model_dump_json(indent=2))

    # 示例2: 仅包含必填字段
    example2 = RagInput(
        query="推荐一本书"
    )
    rich.print("\n示例2:", example2.model_dump_json(indent=2))
