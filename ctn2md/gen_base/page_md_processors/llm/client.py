"""
LLM客户端实现
"""

import logging
import os
import hashlib
import msgpack
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from ctn2md.gen_base.page_md_processors.llm.schemas import DocumentAnalysis
from ctn2md.md_info.md_info_base import MdInfo

logger = logging.getLogger(__name__)

class LlmClient:
    """LLM客户端
    处理与LLM的交互，包括缓存、错误处理等
    """
    
    def __init__(self, md_info: Optional[MdInfo] = None):
        """初始化客户端
        
        Args:
            md_info: 文档信息对象，用于获取缓存目录
        """
        self.md_info = md_info
        self.cache_dir = md_info.get_cache_dir() if md_info else None
        
    def _get_cache_path(self, prompt: str) -> Optional[str]:
        """获取缓存文件路径
        
        Args:
            prompt: 分析提示词
            
        Returns:
            缓存文件路径，如果未设置缓存目录则返回None
        """
        if not self.cache_dir:
            return None
            
        # 使用prompt的hash作为缓存文件名
        prompt_hash = hashlib.sha1(prompt.encode()).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"llm_analysis_{prompt_hash}.msgpack")
        
    def analyze_document(self, prompt: str) -> DocumentAnalysis:
        """分析文档
        
        Args:
            prompt: 分析提示词
            
        Returns:
            文档分析结果
            
        Note:
            使用msgpack缓存结果到文件系统，避免重复调用
        """
        # 获取缓存路径
        cache_path = self._get_cache_path(prompt)
        
        # 如果设置了缓存目录，尝试读取缓存
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = msgpack.unpack(f)
                    # 将缓存数据转换为DocumentAnalysis对象
                    return DocumentAnalysis.model_validate(cache_data)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
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
            result = DocumentAnalysis(**test_response)
            
            # 如果设置了缓存目录，保存缓存
            if cache_path:
                try:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, 'wb') as f:
                        # 将DocumentAnalysis对象转换为dict并序列化
                        msgpack.pack(result.model_dump(), f)
                except Exception as e:
                    logger.warning(f"Failed to save cache: {e}")
            
            return result
            
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
    print(result.model_dump_json(indent=2, ensure_ascii=False)) 