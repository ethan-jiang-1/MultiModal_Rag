from dotenv import load_dotenv 
import logging
import random
import rich
from typing import Optional, List
from pydantic import BaseModel, Field

load_dotenv()

from mrag_vdb.utils.util_logging import setup_logger_handlers, get_logger_progress
from mrag_vdb.query.query2section_raw import query2section_raw_on_rag_context
from mrag_vdb.rerank.query2section_reranked import query2sortedsections_reranked
from mrag_vdb.knowledge.query2knowledge import gen_answer_from_knowledge_snippets, form_knowledge_snippets
from mrag_vdb.knowledge.query2knowledge import query_rewerite, compose_rag_answer
from mrag_vdb.common.runtime_settings import KbNameSel
from mrag_vdb.dto.rag_input import RagInput
from mrag_vdb.dto.rag_context import RagContext
from mrag_vdb.dto.rag_answer import RagAnswer

setup_logger_handlers()
logger_prg = get_logger_progress()

class ProgressStep(BaseModel):
    """Progress step information"""
    # "stepN: percentage: task_name: extra_info"
    step: str
    progress: int  # percentage
    task_name: str
    extra_info: Optional[str] = None

class RagResponse(BaseModel):
    """
    Complete response model that wraps RagAnswer and includes additional metadata
    """
    status: str = Field(
        default="success",
        description="Response status (success/failed)"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status is failed"
    )
    req_id: int = Field(
        description="Unique request identifier"
    )
    user_input: str = Field(
        description="Original user query"
    )
    rag_answer: RagAnswer = Field(
        description="Core RAG answer and sources"
    )
    progress_steps: List[ProgressStep] = Field(
        default_factory=list,
        description="List of progress steps during processing"
    )

    def add_progress(self, step: str, progress: int, task_name: str, extra_info: Optional[str] = None):
        """Add a progress step"""
        self.progress_steps.append(ProgressStep(
            step=step,
            progress=progress,
            task_name=task_name,
            extra_info=extra_info
        ))
        # "stepN; percentage: task_name: extra_info"
        if extra_info is None:
            logger_prg.info(f"{step}: {progress}%: {task_name}")
        else:
            logger_prg.info(f"{step}: {progress}%: {task_name}:{extra_info}")

    @classmethod
    def from_success(cls, req_id: int, user_input: str, rag_answer: RagAnswer) -> "RagResponse":
        """Factory method for successful responses"""
        response = cls(
            status="success",
            req_id=req_id,
            user_input=user_input,
            rag_answer=rag_answer
        )
        return response

    @classmethod
    def from_error(cls, req_id: int, user_input: str, error_msg: str) -> "RagResponse":
        """Factory method for failed responses"""
        response = cls(
            status="failed",
            error_message=error_msg,
            req_id=req_id,
            user_input=user_input,
            rag_answer=RagAnswer(answer="", answer_referenced="")
        )
        return response

def do_core_query(user_input: str, kb_name: Optional[str] = None, limit: int = 10) -> RagResponse:
    req_id = random.randint(10000, 99999)
    response = RagResponse(
        req_id=req_id, 
        user_input=user_input, 
        rag_answer=RagAnswer(answer="", answer_referenced="")
    )
    
    try:
        if kb_name is None:
            kb_name = KbNameSel.get_kbname()

        rag_input = RagInput(query=user_input, 
                             preferred_kbnames=[kb_name])
        rag_context = RagContext(input=rag_input)
        
        response.add_progress("step1", 10, f"选择知识库:{kb_name}")
        logging.info(f"do_core_query: {user_input} on {kb_name}")

        # Query preparation
        response.add_progress("step2", 20, "准备查询(改写)")
        rag_context = query_rewerite(rag_context)
        
        # Knowledge retrieval
        response.add_progress("step3", 30, "召回相关知识(raw)")
        scored_sections_raw = query2section_raw_on_rag_context(rag_context)
        if scored_sections_raw is None:
            return RagResponse.from_error(req_id, user_input, "ERROR: retrieval knowledge is None")
        
        # Reranking
        response.add_progress("step4", 40, "召回相关知识(rerank)")
        scored_sections_reranked = query2sortedsections_reranked(rag_context, scored_sections_raw)
        
        # Knowledge organization
        response.add_progress("step5", 50, "组织整理知识")
        knowledge_snippets = form_knowledge_snippets(rag_context, scored_sections_reranked)
        
        # Generate answer
        response.add_progress("step6", 60, "组织回答#综合知识(文本)")
        resp = gen_answer_from_knowledge_snippets(rag_context, knowledge_snippets)
        if resp is None:
            return RagResponse.from_error(req_id, user_input, "ERROR: llm response is None")
        
        # Process images
        response.add_progress("step7", 80, "组织回答#综合知识(图像)")
        rag_answer = compose_rag_answer(rag_context, resp, scored_sections_reranked)
        if rag_answer is None:
            return RagResponse.from_error(req_id, user_input, "ERROR: rag answer generation failed")
        
        rich.print(rag_answer)

        # 直接更新现有response的rag_answer
        response.rag_answer = rag_answer
        response.add_progress("step8", 95, "完成回答")
        return response
        
    except Exception as ex:
        logging.exception(ex)
        return RagResponse.from_error(req_id, user_input, str(ex))



if __name__ == "__main__":
    #from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    #user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")
    user_inputs.append("椅背板与旁侧板的保留运动间隙是多少？")

    for user_input in user_inputs:
        try:
            rag_response = do_core_query(user_input, kb_name="mrag")
            rich.print(rag_response)
        except Exception as ex:
            logging.exception(ex)
