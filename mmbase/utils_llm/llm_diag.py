import logging
import json
import os
from typing import List, Any, Dict, Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv()

# Constants
ENV_QUESTION_NUM = "ENV_QUESTION_NUM"
LLM_DIAG_SEP = "\n\n~~~~--------~~~~\n\n"
LLM_DIAG_LED = "~~~~"
LLM_DIAG_ROL = ":::: "
DEFAULT_TOP_P = 0.9
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MODEL = "gpt4o"

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
