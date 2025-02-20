from typing import Optional, List
from pydantic import BaseModel, Field

from mrag_vdb.dto.rag_answer import RagAnswer
from mmbase.utils.util_logging import get_logger_progress
from mrag_app.utils._app_qa_progress_step import ProgressStep

logger_prg = get_logger_progress()

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

if __name__ == "__main__":
    import rich
    from mmbase.utils.util_logging import setup_logger_handlers
    
    # 设置日志
    setup_logger_handlers()
    
    # 创建一个成功的响应
    success_answer = RagAnswer(
        answer="这是一个测试回答",
        answer_referenced="这是一个带引用的回答"
    )
    success_response = RagResponse.from_success(
        req_id=12345,
        user_input="测试问题",
        rag_answer=success_answer
    )
    
    # 添加进度步骤
    success_response.add_progress("step1", 0, "开始查询")
    success_response.add_progress("step2", 50, "处理中", "正在生成回答")
    success_response.add_progress("step3", 100, "完成查询")
    
    rich.print("\n[bold blue]成功响应示例:[/bold blue]")
    rich.print(success_response)
    
    # 创建一个错误响应
    error_response = RagResponse.from_error(
        req_id=12346,
        user_input="错误测试",
        error_msg="测试错误信息"
    )
    error_response.add_progress("error", 0, "查询失败", "发生错误")
    
    rich.print("\n[bold red]错误响应示例:[/bold red]")
    rich.print(error_response) 