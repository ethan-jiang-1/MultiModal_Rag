from openai import AzureOpenAI
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import sys
import os
import json_repair
import openai 
import requests
import logging
import time
import csv
import rich 
from datetime import datetime
from typing import Optional, List, Dict
#import json

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from ctn2md.utils_llm.llm_base_oss import upload_image_to_oss

"""
| Task            | `temperature`  | `top_p`       | Comment                                                              |
|-----------------|----------------|---------------|----------------------------------------------------------------------|
| SQL Generation  | `0.0` - `0.2`  | `0.9` - `1.0` | Prioritizes precision and correctness in SQL generation.             |
| Analysis        | `0.3` - `0.6`  | `0.85` - `1.0`| Balances logic with some creativity for diverse perspectives.        |
| Report          | `0.5` - `0.7`  | `0.9` - `1.0` | Supports natural, varied language for detailed report writing.       |

"""

DEFAULT_RETRY_NUM = 5

def get_gpt_messages(system_prompt:str, user_prompt:str) -> list:
    messages=[
        {
            "role": "system",
            "content": str(system_prompt)
        },
        {
            "role": "user",
            "content": str(user_prompt)
        },
    ]
    return messages



def get_gpt_messages_multimodal(system_prompt:str, user_prompt:str, image_path:str) -> list:
    """生成支持多模态的消息结构"""
    img_url = upload_image_to_oss(image_path)
    
    # 构造多模态消息
    messages = []
    if system_prompt is not None:
        messages.append(
            {
                "role": "system",
                "content": [{"type": "text", "text": str(system_prompt)}] 
            })
    messages.append(
        {
            "role": "user",
            "content": [{"type": "text", "text": str(user_prompt)},
                        {"type": "image_url",  # 明确指定类型为 image
                         "image_url": {"url": img_url}}]
        }
    )
    
    return messages


def get_azure_gpt_client() -> AzureOpenAI:
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version=os.environ.get("AZURE_OPENAI_VERSION"))
    return client


def get_dashscope_client() -> OpenAI:
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return client

def get_ark_client() -> OpenAI:
    client = OpenAI(
        api_key=os.environ.get("ARK_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    )

    return client

def jsons_load_repair(content:str) -> dict:
    resp = json_repair.repair_json(content, 
                                   ensure_ascii=True, 
                                   return_objects=True)
    return resp

class MonitorContextLLM:
    LEADING_PREFIX = "ctn"

    @classmethod
    def _get_monitor_filename(cls, model:str) -> str:
        dir_root = os.path.dirname(find_dotenv())
        dir_logs = os.path.join(dir_root, "logs")
        os.makedirs(dir_logs, exist_ok=True)
        if model.startswith("gpt"):
            fname = f"{cls.LEADING_PREFIX}_monitor_gpt.csv"
        elif model.startswith("qwen"):
            fname = f"{cls.LEADING_PREFIX}_monitor_qwen.csv"
        elif model.startswith("ep-"):
            fname = f"{cls.LEADING_PREFIX}_monitor_ark.csv"
        else:
            fname = f"{cls.LEADING_PREFIX}_monotor_ukn.csv"
        filename = os.path.join(dir_logs, fname)
        return filename

    def __init__(self, messages:list, model:str, track_id:str, attempt:int):
        self.messages = messages
        self.model = model
        self.track_id = track_id
        self.attempt = attempt

        self.d0 = None
        self.d1 = None
        self.response = None

    def __enter__(self):
        logging.info(f"MonitorContextLLM enter model:{self.model}")
        self.d0 = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info(f"MonitorContextLLM enter model:{self.model}")
        self.d1 = time.time()
        self._monitor_call(exc_type)
        if exc_type is not None:
            logging.exception(self.track_id)

    def _monitor_call(self, exc_type:Exception):
        try:
            filename = self._get_monitor_filename(self.model)
            
            # Check if file exists and is empty
            file_exists = os.path.exists(filename)
            file_empty = file_exists and os.path.getsize(filename) == 0
            
            dt = self.d1 - self.d0
            dt = round(dt, 2)
            self.d0 = round(self.d0, 2)
            sec_span = round(dt, 2)
            ts0 = datetime.fromtimestamp(self.d0).strftime("%Y%m%d:%H:%M:%S")
 
            model_actual = self.model
            
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
                # Write headers if file is empty or doesn't exist
                if not file_exists or file_empty:
                    writer.writerow(['timestamp', 'finish_reason', 'model_requested', 'model_actual', 
                                   'sec_span', 'total_tokens', 'prompt_tokens', 'completion_tokens', 
                                   'token_per_ms', 'track_id', 'attempt'])
                
                if self.response is not None:
                    choice0 = self.response.choices[0]
                    finish_reason = choice0.finish_reason
                    model_requested = self.model
                    model_actual = self.response.model
                    usage = self.response.usage
                    completion_tokens = usage.completion_tokens
                    output_ratio_per_sec = round(float(completion_tokens) / sec_span, 2)
                    token_per_ms = round((1.0/output_ratio_per_sec) * 1000.0, 2)
                    
                    writer.writerow([
                        ts0,                                    # 字符串
                        finish_reason,                          # 字符串
                        model_requested,                        # 字符串
                        model_actual,                          # 字符串
                        sec_span,                              # 数值
                        usage.total_tokens,                    # 数值
                        usage.prompt_tokens,                   # 数值
                        usage.completion_tokens,               # 数值
                        token_per_ms,                         # 数值
                        str(self.track_id),                    # 字符串
                        self.attempt                           # 数值
                    ])
                else:
                    writer.writerow([
                        ts0,                # 字符串
                        str(exc_type),      # 字符串
                        self.model,         # 字符串
                        model_actual,       # 字符串
                        sec_span,           # 数值
                        0,                  # 数值
                        0,                  # 数值
                        0,                  # 数值
                        0.0,                # 数值
                        str(self.track_id), # 字符串
                        self.attempt        # 数值
                    ])

        except Exception as ex:  # noqa
            logging.exception(ex)

def chat_gpt_json(
    messages: List[Dict[str, str]], 
    model: str = "gpt-4o-mini", 
    temperature: float = 0.1, 
    top_p: float = 0.9,
    retries: int = DEFAULT_RETRY_NUM,
    backoff_factor: float = 2,
    backoff_sec: float = 1,
    delay_base_sec: float = 5,
    track_id: Optional[str] = None,
    client: Optional[OpenAI] = None,
) -> dict:
    """
    使用GPT模型进行JSON格式的对话。

    Args:
        messages: 对话消息列表
        model: 模型名称
        temperature: 温度参数
        top_p: top-p采样参数
        retries: 重试次数
        backoff_factor: 退避因子
        backoff_sec: 初始退避时间
        delay_base_sec: 基础延迟时间
        track_id: 追踪ID
        client: OpenAI客户端实例，如果为None则使用默认Azure客户端

    Returns:
        dict: GPT响应的JSON内容

    Raises:
        ValueError: 参数验证失败
        openai.BadRequestError: API请求错误
    """
    if not messages:
        raise ValueError("Messages cannot be empty")

    client = client or get_azure_gpt_client()
    
    for attempt in range(retries):
        try:
            with MonitorContextLLM(messages, model, track_id, attempt) as mc:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    response_format={"type": "json_object"})
                mc.response = response
                resp = jsons_load_repair(response.choices[0].message.content)
                return resp
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logging.error(f"Error on attempt {attempt+1}: {str(e)}")
            if attempt == retries:
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logging.info(f"Retrying after backoff: {backoff_sec} seconds...")
            time.sleep(backoff_sec)
        except (openai.BadRequestError) as e:
            logging.exception(e)
            raise

def chat_gpt_plain(
    messages: list,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    top_p: float = 0.9,
    retries: int = DEFAULT_RETRY_NUM,
    backoff_factor: float = 2,
    backoff_sec: float = 1,
    delay_base_sec: float = 5,
    track_id: Optional[str] = None,
    client: Optional[OpenAI] = None
) -> str:
    if client is None:
        client = get_azure_gpt_client()
    for attempt in range(retries):
        try:
            with MonitorContextLLM(messages, model, track_id, attempt) as mc:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p)
                mc.response = response
                return response.choices[0].message.content
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logging.error(f"Error on attempt {attempt+1}: {str(e)}")
            if attempt == retries:
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logging.info(f"Retrying after backoff: {backoff_sec} seconds...")
            time.sleep(backoff_sec)
        except (openai.BadRequestError) as e:
            logging.exception(e)
            raise


if __name__ == "__main__":
    messages = get_gpt_messages("", "hi, response in json")
    resp = chat_gpt_json(messages=messages, model="gpt-4o")
    rich.print(resp)

    messages = get_gpt_messages("", "hi, response in json")
    resp = chat_gpt_json(messages=messages, model="gpt-4o-mini")
    rich.print(resp)

    messages = get_gpt_messages("", "hi, response in text")
    resp = chat_gpt_plain(messages=messages, model="gpt-4o")
    rich.print(resp)

    messages = get_gpt_messages("", "hi, response in text")
    resp = chat_gpt_plain(messages=messages, model="gpt-4o-mini")
    rich.print(resp)