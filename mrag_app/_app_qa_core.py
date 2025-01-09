from typing import Optional
from pydantic import BaseModel, Field
import logging
import rich
import random

from mrag_app._rag_core_query import do_core_query as _do_core_query
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer

class _QueryState(BaseModel):
    """
    Query state for main loop
    """
    response: Optional[RagResponse] = Field(
        default=None,
        description="Current response"
    )

    @classmethod
    def get_response(cls) -> Optional[RagResponse]:
        """Get current response"""
        return cls.response

    @classmethod
    def set_response(cls, response: RagResponse):
        """Set current response"""
        cls.response = response

    @classmethod
    def reset(cls):
        """Reset state"""
        cls.response = None

def main_loop_gradio(user_input: str, kb_name: Optional[str] = None, limit: int = 10) -> None:
    """
    Main loop for gradio interface
    """
    try:
        # 初始化进度
        response = RagResponse(
            req_id=random.randint(10000, 99999),
            user_input=user_input,
            rag_answer=RagAnswer(answer="", answer_referenced="")
        )
        response.add_progress("step0.5", 5, "选择LLM引擎")
        _QueryState.set_response(response)

        # 执行查询
        response = _do_core_query(user_input, kb_name=kb_name, limit=limit)
        response.add_progress("step10", 100, "查询退出")
        _QueryState.set_response(response)
    except Exception as ex:
        logging.exception(ex)
        response = RagResponse.from_error(
            req_id=random.randint(10000, 99999),
            user_input=user_input,
            error_msg=str(ex)
        )
        response.add_progress("error", 0, f"查询异常#{str(ex)}")
        _QueryState.set_response(response)

def get_rag_response_from_main_loop() -> Optional[RagResponse]:
    """Get response from main loop"""
    return _QueryState.get_response()

def reset_rag_response_for_main_loop():
    """Reset response for main loop"""
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
