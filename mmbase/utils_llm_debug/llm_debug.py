import logging
import json
#import os
import rich 
from typing import List, Any, Dict, Tuple
from dotenv import load_dotenv
from deepdiff import DeepDiff

load_dotenv()

from mmbase.utils_llm.llm_base import chat_gpt_json, chat_gpt_plain
from mmbase.utils_llm.llm_base import get_azure_gpt_client as _get_azure_gpt_client
from mmbase.utils_llm.llm_base import get_dashscope_client as _get_dashscope_client
from mmbase.utils_llm.llm_base import get_ark_client as _get_ark_client
from mmbase.utils_llm_debug.llm_diag import LLM_DIAG_SEP, LLM_DIAG_LED, LLM_DIAG_ROL

def _json_loads_repair(response_json_string: str) -> dict:
    """修复并解析可能损坏的JSON字符串"""
    try:
        import json_repair
        return json_repair.repair_json(response_json_string, return_objects=True)
    except Exception as ex:
        logging.error(f"JSON repair failed: {ex}")
        raise

def _load_llm_diag(filename: str) -> tuple[List[dict], Any, dict]:
    """加载LLM对话记录
    
    Args:
        filename: 对话记录文件路径
    
    Returns:
        (messages, answer, extra): 消息列表、响应内容和元数据
    
    Raises:
        ValueError: 文件格式错误时抛出
    """
    # 读取文件内容
    with open(filename, 'r', encoding='utf-8') as f:
        file_content = "".join(f.readlines())
    
    # 分割内容部分
    sections = file_content.split(LLM_DIAG_SEP)
    if len(sections) != 3:
        raise ValueError("Invalid file format: expected 3 sections")

    message_raw, answer_raw, extra_raw = [s.strip() for s in sections]

    # 解析消息
    messages = []
    raw_messages = message_raw.split(LLM_DIAG_LED)
    role, role_msg = None, None
    
    for raw_message in raw_messages:
        if not raw_message or LLM_DIAG_ROL not in raw_message:
            continue
            
        part1, part2 = raw_message.split(LLM_DIAG_ROL)
        if part1 == "role":
            role = part1
            role_msg = part2.strip()
        elif part1 == "content":
            content = part1
            content_msg = part2.strip()
            messages.append({role: role_msg, content: content_msg})
        else:
            raise ValueError(f"Invalid message format: {raw_message}")

    # 解析响应
    try:
        answer = json.loads(answer_raw)
    except json.JSONDecodeError:
        answer = answer_raw.strip()

    # 解析元数据
    extra = _json_loads_repair(extra_raw)
    if not isinstance(extra, dict):
        raise ValueError("Invalid metadata format")
    
    if extra.get("ver", 0) < 1.0:
        raise ValueError("Unsupported version")
    
    return messages, answer, extra 

def do_diag_reproduce(llm_diag_pathname: str) -> Tuple[Dict, Dict, DeepDiff]:
    """
    重现和比较LLM诊断结果。

    Args:
        llm_diag_pathname: LLM诊断文件的路径

    Returns:
        Tuple包含:
            - answer_old: 原始回答
            - answer_new: 新的回答
            - answer_changed: 两个回答的差异
    """
    messages, answer_old, extra = _load_llm_diag(llm_diag_pathname)

    # 默认参数设置
    params = {
        "top_p": 0.9,
        "temperature": 0.3,
        "model": "gpt4o",
        "is_json_response": True
    }

    # 如果extra存在，更新参数
    if extra is not None:
        params.update({
            "top_p": extra.get("top_p", params["top_p"]),
            "temperature": extra.get("temperature", params["temperature"]),
            "model": extra.get("model", params["model"]),
            "is_json_response": extra.get("is_json_response", params["is_json_response"])
        })

    client = None 
    if params["model"].startswith("gpt"):
        client = _get_azure_gpt_client()
    elif params["model"].startswith("qwen"):
        client = _get_dashscope_client()
    elif params["model"].startswith("qp"):
        client = _get_ark_client()
    else:
        raise ValueError(f"Unsupported model: {params['model']}")
    
    # 根据响应类型选择不同的调用方法
    if params["is_json_response"]:
        answer_new = chat_gpt_json(
            messages, 
            model=params["model"],
            top_p=params["top_p"],
            temperature=params["temperature"],
            track_id="llm_ddr_json",
            client=client
        )
    else:
        answer_new = chat_gpt_plain(
            messages,
            model=params["model"],
            top_p=params["top_p"],
            temperature=params["temperature"],
            track_id="llm_ddr_plain",
            client=client
        )

    # 打印结果
    rich.print("[bold blue]Original Answer:[/bold blue]")
    rich.print(answer_old)
    print()
    rich.print("[bold green]New Answer:[/bold green]")
    rich.print(answer_new)
    print()

    # 比较差异
    answer_changed = DeepDiff(answer_old, answer_new)
    rich.print("[bold yellow]Differences:[/bold yellow]")
    rich.print(answer_changed)
    print()

    return answer_old, answer_new, answer_changed
