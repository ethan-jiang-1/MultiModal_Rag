import os
import copy
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uuid import uuid4
from multiprocessing import Manager
from contextlib import asynccontextmanager
from HiQA.qa_core import do_core_query, _get_root_dir
import subprocess
import asyncio

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 允许所有域名
#     allow_credentials=True,
#     allow_methods=["*"],  # 允许所有方法
#     allow_headers=["*"],  # 允许所有头部
# )
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化共享状态
    manager = Manager()
    tasks = manager.dict()

    # 将共享状态存储在 app.state 中，方便应用其他地方访问
    app.state.tasks = tasks

    yield  # 应用启动时的代码

    manager.shutdown()  # 应用关闭时的清理操作


# 创建带有生命周期管理的 FastAPI 应用实例
app = FastAPI(lifespan=lifespan)

static_file_base = os.path.join(_get_root_dir(), "HiQA/datasets")
app.mount("/multimodalrag/static", StaticFiles(directory=static_file_base), name="static")

@app.get("/multimodalrag/")
def make_report():
    return "hello from MultiModal-Rag"


@app.get("/multimodalrag/update_and_reload/")
async def update_and_reload():
    try:
        # 执行shell指令，调用git pull
        result = subprocess.run(
            ["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # 打印执行结果
        message = result.stdout.decode()
        error = result.stderr.decode()
        print("stdout:", message)
        print("stderr:", error)
        await asyncio.sleep(3)

        return "Update and reload successfully"
    except Exception as e:
        print("Failed to update and reload:", e)
        # logger.error(f"Failed to update and reload: {e}")
        return '''Failed to update and reload
            {e}
        '''


class RequestRag(BaseModel):
    question: str


@app.post("/multimodalrag/query/")
def make_report(args: RequestRag, request: Request, background_tasks: BackgroundTasks):
    task_id = start_background_task(args.question, request.app.state.tasks, background_tasks)
    return {"task_id": task_id}


@app.get("/multimodalrag/check_status/{task_id}")
async def check_status(task_id: str, request: Request):
    return request.app.state.tasks.get(task_id, "Task not found")


# def update_task_status(task_id: str, status: str, progress: int, message: str):
#     app.state.tasks[task_id] = {
#         "status": status,
#         "progress": progress,
#         "message": message,
#     }


def _fix_result(rslt: dict) -> dict:
    image_path_base = os.path.normpath(os.path.join(_get_root_dir(), "HiQA/datasets"))

    def _fix_path(raw_path: str) -> str:
        norm_path = os.path.normpath(raw_path)
        return os.path.relpath(norm_path, image_path_base).replace('\\', '/')
    
    ret = copy.deepcopy(rslt)
    for item in ret.get("lst_image_n_title", []):
        item["src"] = _fix_path(item["image"])

    temp = []
    for url in ret.get("lst_source_matches", []):
        temp.append({
            "src": _fix_path(url),
            "filename": os.path.basename(url)
        })
    ret["lst_source_matches"] = temp
    
    return ret



# 这是一个长时间运行的任务函数
def call_do_query(question: str, tasks, task_id: str):
    try:
        rslt = do_core_query(question)
        rslt = _fix_result(rslt)
        if tasks is not None:
            tasks[task_id] = {
                "status": "completed",
                "progress": 100,
                "question": question,
                "content": rslt,
            }
            return tasks[task_id]
        else:
            return rslt
    except Exception as e:
        tasks[task_id] = {"status": "failed", "error": str(e)}
        return tasks[task_id]


# 这是一个启动后台任务的函数
def start_background_task(question: str, tasks, background_tasks: BackgroundTasks):
    task_id = uuid4().hex  # 生成唯一的任务 ID
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "查询中..."
    }  # 初始化任务状态为 pending
    # 使用 BackgroundTasks 启动后台任务
    background_tasks.add_task(call_do_query, question, tasks, task_id)
    return task_id


def open_result_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


if __name__ == "__main__":
    import sys
    import json

    sys.path.append(".")
    sys.path.append("..")

    from HiQA.qa_core import do_core_query, _get_root_dir

    rslt = call_do_query("前后座椅H点参考距离是多少？", None, "test")
    print(json.dumps(rslt))