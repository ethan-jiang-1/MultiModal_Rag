"""
LLM客户端实现
"""

import logging
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

from ctn2md.gen_base.page_md_processors.llm.schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

class LlmClient:
    """LLM客户端
    处理与LLM的交互，包括缓存、错误处理等
    """
    
    def __init__(self):
        """初始化客户端"""
        # TODO: 初始化实际的LLM客户端
        pass
        
    @lru_cache(maxsize=100)
    def analyze_document(self, prompt: str) -> DocumentAnalysis:
        """分析文档
        
        Args:
            prompt: 分析提示词
            
        Returns:
            文档分析结果
            
        Note:
            使用lru_cache缓存结果，避免重复调用
        """
        try:
            # TODO: 实际的LLM调用
            # 这里先返回测试数据
            test_response = {
                "remove_actions": [
                    {
                        "page": 1,
                        "lines": [1, 2],
                        "reason": "页眉"
                    }
                ],
                "merge_actions": [
                    {
                        "type": "table",
                        "pages": [1, 2],
                        "line_ranges": {
                            "1": [{"start": 15, "end": 20}],
                            "2": [{"start": 1, "end": 5}]
                        }
                    }
                ]
            }
            
            # 使用pydantic模型验证和转换
            return DocumentAnalysis(**test_response)
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # 返回空的分析结果
            return DocumentAnalysis() 

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试代码
    client = LlmClient()
    
    # 测试分析
    test_prompt = """
    <<<< 第1页 >>>>
    [P1-L1] 页眉内容
    [P1-L2] 正文内容
    [P1-L3] | 表头1 | 表头2 |
    [P1-L4] | --- | --- |
    <<<< 第1页 结束 >>>>
    
    <<<< 第2页 >>>>
    [P2-L1] | 数据1 | 数据2 |
    [P2-L2] 页脚内容
    <<<< 第2页 结束 >>>>
    """
    
    result = client.analyze_document(test_prompt)
    print("分析结果:")
    print(result.json(indent=2, ensure_ascii=False)) 