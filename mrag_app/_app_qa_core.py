from dotenv import load_dotenv
import os
import logging
import rich
from typing import Optional
import random
load_dotenv()

from mrag_vdb.utils.util_logging import setup_logger_handlers, get_logger_progress
from mrag_vdb.utils.util_file import get_root_dir
from mrag_app._qa_core import do_core_query as _do_core_query, RagResponse, RagAnswer
from mrag_vdb.common.runtime_settings import KbNameSel, ModelGptSel, RetrievalNum

setup_logger_handlers()
logger_prg = get_logger_progress()

def _ensure_working_dir():
    dir_root = get_root_dir()
    os.chdir(dir_root)
    return dir_root
   
_ensure_working_dir()

class _QueryState:
    """Manages the state of the current query"""
    _current_response: Optional[RagResponse] = None
    
    @classmethod
    def set_response(cls, response: RagResponse):
        cls._current_response = response
    
    @classmethod
    def get_response(cls) -> Optional[RagResponse]:
        return cls._current_response
        
    @classmethod
    def reset(cls):
        """Reset the query state to initial state"""
        cls._current_response = None

def main_loop_gradio(user_input: str, kb_name: Optional[str] = None) -> None:
    """Main query processing loop for Gradio interface"""
    try:
        # 初始化空的响应对象
        response = RagResponse(
            req_id=random.randint(10000, 99999),
            user_input=user_input,
            rag_answer=RagAnswer(answer="", answer_referenced="")
        )
        
        # 立即设置初始响应，这样UI可以立即看到状态
        _QueryState.set_response(response)
        
        # 添加初始进度
        response.add_progress("step0.5", 5, f"查询进入:选择LLM引擎:{ModelGptSel.get_gpt_model()}")
        
        if kb_name is None:
            kb_name = KbNameSel.get_kbname()
        limit = RetrievalNum.get_retrieval_num()

        # 执行核心查询
        response = _do_core_query(user_input, kb_name=kb_name, limit=limit)
        response.add_progress("step10", 100, "查询退出")
        
    except Exception as ex:
        logging.exception(ex)
        response = RagResponse.from_error(
            req_id=random.randint(10000, 99999),
            user_input=user_input,
            error_msg=str(ex)
        )
        response.add_progress("error", 0, f"查询异常#{str(ex)}")
    
    finally:
        # 确保最终状态被更新
        _QueryState.set_response(response)

def get_rag_response_from_main_loop() -> Optional[RagResponse]:
    """Get the current query response"""
    return _QueryState.get_response()

def reset_rag_response_for_main_loop() -> None:
    """Reset the query state"""
    _QueryState.reset()


if __name__ == "__main__":
    #from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")

    for user_input in user_inputs:
        try:
            main_loop_gradio(user_input)
            rag_response = get_rag_response_from_main_loop()
            rich.print(rag_response)
        except Exception as ex:
            logging.exception(ex)
