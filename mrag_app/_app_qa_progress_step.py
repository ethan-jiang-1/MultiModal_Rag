from typing import Optional
from pydantic import BaseModel, Field

class ProgressStep(BaseModel):
    """Progress step information"""
    # "stepN: percentage: task_name: extra_info"
    step: str
    progress: int = Field(ge=0, le=100)  # percentage
    task_name: str
    extra_info: Optional[str] = None 

if __name__ == "__main__":
    import rich
    
    # 创建一个进度步骤序列
    steps = [
        ProgressStep(step="step1", progress=0, task_name="开始任务"),
        ProgressStep(step="step2", progress=50, task_name="处理中", extra_info="正在处理数据"),
        ProgressStep(step="step3", progress=100, task_name="完成任务")
    ]
    
    # 打印并验证每个步骤
    for step in steps:
        rich.print(f"[blue]当前步骤:[/blue] {step.step}")
        rich.print(f"[green]进度:[/green] {step.progress}%")
        rich.print(f"[yellow]任务:[/yellow] {step.task_name}")
        if step.extra_info:
            rich.print(f"[magenta]额外信息:[/magenta] {step.extra_info}")
        rich.print("---") 