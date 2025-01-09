
import logging
import json
import os
import rich 
from typing import List, Any, Dict, Optional, Tuple
from dotenv import load_dotenv, find_dotenv
from deepdiff import DeepDiff
from openai import AzureOpenAI, OpenAI

load_dotenv()

from mmbase.utils_llm.llm_base import chat_gpt_json, chat_gpt_plain

# Constants
ENV_QUESTION_NUM = "ENV_QUESTION_NUM"
LLM_DIAG_SEP = "\n\n~~~~--------~~~~\n\n"
LLM_DIAG_LED = "~~~~"
LLM_DIAG_ROL = ":::: "
DEFAULT_TOP_P = 0.9
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MODEL = "gpt4o"

def _get_azure_gpt_client() -> AzureOpenAI:
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version=os.environ.get("AZURE_OPENAI_VERSION"))
    return client


def _get_dashscope_client() -> OpenAI:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return client


def _get_ark_client() -> OpenAI:
    client = OpenAI(
        api_key=os.environ.get("ARK_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
    return client

def _get_root_dir() -> str:
    """获取项目根目录路径"""
    return os.path.abspath(os.path.dirname(find_dotenv()))

def _json_loads_repair(response_json_string: str) -> dict:
    """修复并解析可能损坏的JSON字符串"""
    try:
        import json_repair
        return json_repair.repair_json(response_json_string, return_objects=True)
    except Exception as ex:
        logging.error(f"JSON repair failed: {ex}")
        raise

def get_chat_messages(system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
    """生成标准的对话消息格式
    
    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
    
    Returns:
        包含system和user消息的列表
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def set_question_num(question_num: int) -> None:
    """设置当前问题编号"""
    os.environ[ENV_QUESTION_NUM] = str(question_num)

def get_question_num() -> int:
    """获取当前问题编号"""
    return int(os.environ.get(ENV_QUESTION_NUM, "0"))

def get_next_question_num() -> int:
    """获取并设置下一个问题编号"""
    question_num = get_question_num()
    question_num += 1
    set_question_num(question_num)
    return question_num

def save_llm_diag_messages(
    messages: List[dict],
    response: Any,
    model: str = "gpt4-o",
    top_p: float = 0.8,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    prefix: Optional[str] = None,
    is_json_response: bool = True,
    question_num: Optional[int] = None
) -> None:
    """保存LLM对话记录
    
    Args:
        messages: 对话消息列表
        response: LLM响应内容
        model: 模型名称
        top_p: top-p采样参数
        temperature: 温度参数
        max_tokens: 最大token数
        prefix: 文件名前缀
        is_json_response: 响应是否为JSON格式
        question_num: 问题编号，若为None则使用当前编号
    """
    if not messages:
        raise ValueError("Messages cannot be empty")
    try:
        if question_num is None:
            question_num = get_question_num()
        
        # 创建输出目录
        output_dir = os.path.join(_get_root_dir(), "_work/llm_dialogs")
        os.makedirs(output_dir, exist_ok=True)

        # 生成输出文件路径
        llm_fname = os.path.join(output_dir, f"llm_{prefix}_q{question_num}.txt")
        logging.info(f"SLD: last llm_diag saved at {llm_fname}")

        # 写入对话记录
        with open(llm_fname, 'w', encoding='utf-8') as f:
            # 写入消息
            for message in messages:
                if isinstance(message, dict):
                    for key, val in message.items():
                        f.write(f"{LLM_DIAG_LED}{key}{LLM_DIAG_ROL}{val}\n")
                    f.write("\n")
                else:
                    f.write(str(message) + "\n")
            f.write(LLM_DIAG_SEP)

            # 写入响应
            if hasattr(response, "choices"):
                response = response.choices[0].message.content
            json.dump(response, f, ensure_ascii=False, indent=4)
            f.write(LLM_DIAG_SEP)

            # 写入元数据
            meta_data = {
                "top_p": top_p,
                "temperature": temperature,
                "is_json_response": is_json_response,
                "model": model,
                "ver": 1.1,
                "max_token": max_tokens
            }
            json.dump(meta_data, f, ensure_ascii=False, indent=4)

        logging.info(f"{llm_fname} saved")
    except Exception as ex:
        logging.exception(ex)

def save_llm_diag_prompt(
    prompt: str,
    response: Any,
    system_prompt: Optional[str] = None,
    model: str = "gpt4-o",
    top_p: float = 0.8,
    temperature: float = 0.2,
    prefix: Optional[str] = None,
    is_json_response: bool = True,
    question_num: Optional[int] = None
) -> None:
    """保存简单提示词对话记录的快捷方法
    
    将prompt和system_prompt转换为标准消息格式后保存
    """
    messages = get_chat_messages(system_prompt or "", prompt)
    return save_llm_diag_messages(
        messages,
        response,
        model=model,
        top_p=top_p,
        temperature=temperature,
        prefix=prefix,
        is_json_response=is_json_response,
        question_num=question_num
    )

def load_llm_diag(filename: str) -> tuple[List[dict], Any, dict]:
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
    messages, answer_old, extra = load_llm_diag(llm_diag_pathname)

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
