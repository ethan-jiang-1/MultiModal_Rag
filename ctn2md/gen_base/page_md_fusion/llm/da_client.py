"""
LLM客户端实现
"""

import logging
import os
import hashlib
import msgpack
import rich
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from mmbase.utils_llm.llm_base import chat_gpt_json, get_gpt_messages
from ctn2md.gen_base.page_md_fusion.llm.da_schemas import DocumentAnalysis
from ctn2md.md_info.md_info_base import MdInfo
from mmbase.utils_llm_debug.llm_diag import save_llm_diag_messages

logger = logging.getLogger(__name__)

class LlmClient:
    """LLM客户端
    处理与LLM的交互，包括缓存、错误处理等
    """
    _question_num = 9000
    
    def __init__(self, md_info: Optional[MdInfo] = None):
        """初始化客户端
        
        Args:
            md_info: 文档信息对象，用于获取缓存目录
        """
        self.md_info = md_info
        self.cache_dir = md_info.get_cache_dir() if md_info else None
        
    def _get_cache_path(self, system_prompt: str, user_prompt: str, model: str) -> Optional[str]:
        """获取缓存文件路径
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称
            
        Returns:
            缓存文件路径，如果未设置缓存目录则返回None
        """
        if not self.cache_dir:
            return None
            
        # 使用prompt的hash作为缓存文件名
        hash_str = f"{system_prompt}_{user_prompt}_{model}"
        prompt_hash = hashlib.sha1(hash_str.encode()).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"llm_analysis_{prompt_hash}.msgpack")
    
    def get_model(self, model_sel: Optional[str] = None) -> str:
        """获取模型名称"""
        model_final = None
        if model_sel:
            model_final = model_sel
        else:
            if self.md_info:
                model_final = self.md_info.get_md_control("mctl_flow_model", "qwen")
            else:
                model_final = "gpt-4o"

        if model_final.startswith("qwen"):
            return "qwen-max"
        elif model_final.startswith("gpt"):
            return "gpt-4o"
        elif model_final.startswith("ark"):
            return "ep-20241220101421-4tj5f"
        else:
            raise ValueError(f"Invalid model: {model_final}")
    
    def analyze_document(self, system_prompt: str, user_prompt: str, using_cache: bool = True, model_sel: Optional[str] = None) -> DocumentAnalysis:
        """分析文档
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            
        Returns:
            文档分析结果
            
        Note:
            使用msgpack缓存结果到文件系统，避免重复调用
        """
        model = self.get_model(model_sel)
        
        # 获取缓存路径
        cache_path = None
        if using_cache:
            cache_path = self._get_cache_path(system_prompt, user_prompt, model)
            
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
            # 构造消息
            messages = get_gpt_messages(system_prompt, user_prompt)
            temperature = 0.1
            top_p = 0.9
            # 调用LLM
            response = chat_gpt_json(
                messages=messages,
                model=model,
                temperature=temperature,  # 分析任务需要高确定性
                top_p=top_p
            )
            save_llm_diag_messages(messages, response, model=model, temperature=temperature, top_p=top_p, question_num=self._question_num, prefix="doc_analysis_gpt")
            self._question_num += 1

            # 使用pydantic模型验证和转换
            rich.print(response)
            result = DocumentAnalysis.model_validate(response)
            
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
            raise e

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    from ctn2md.gen_base.page_md_fusion.llm.marked_content_maker import MarkedContentMaker
    from ctn2md.gen_base.page_md_fusion.llm.action_explainer import ActionExplainer
    from ctn2md.gen_base.page_md_fusion.llm.da_prompts import SYSTEM_PROMPT_DOC_ANALYSIS, USER_PROMPT_DOC_ANALYSIS

    setup_logger_handlers()
    
    pname_info = "_work/ctn2md_papers___paged_md/_info.json"
    #pname_info = "_work/ctn2md_mrag___paged_md/_info.json"
    md_info = MdInfo(pname_info)

    #llm_client = LlmClient(md_info)
    llm_client = LlmClient(md_info)
    
    fnames = md_info.get_fnames_pages()
    #fnames = fnames[:3】

    maker = MarkedContentMaker()
    marked_content, doc_pages = maker.make_marked_content_from_md_info(md_info, fnames)
    #rich.print(marked_content)

    system_prompt = SYSTEM_PROMPT_DOC_ANALYSIS
    user_prompt = USER_PROMPT_DOC_ANALYSIS.replace("{marked_content_from_pages}", marked_content)
    #print(user_prompt)

    das = llm_client.analyze_document(system_prompt, user_prompt, using_cache=False, model_sel="gpt-4o")
    rich.print(das)

    explanation = ActionExplainer.explain_document_analysis(das, doc_pages)
    logger.info("\nDocument Analysis Report:\n%s", explanation)

