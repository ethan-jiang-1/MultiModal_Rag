from openai import AzureOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
import json_repair
import openai 
import httpx
import logging
import rich 
from typing import Optional, List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

from ctn2md.utils_llm.llm_base_monitor import MonitorContextLLM

"""
| Task            | `temperature`  | `top_p`       | Comment                                                              |
|-----------------|----------------|---------------|----------------------------------------------------------------------|
| SQL Generation  | `0.0` - `0.2`  | `0.9` - `1.0` | Prioritizes precision and correctness in SQL generation.             |
| Analysis        | `0.3` - `0.6`  | `0.85` - `1.0`| Balances logic with some creativity for diverse perspectives.        |
| Report          | `0.5` - `0.7`  | `0.9` - `1.0` | Supports natural, varied language for detailed report writing.       |

"""

DEFAULT_RETRY_NUM = 5


def upload_image_to_cloud(image_path: str) -> str:
    """统一的图片上传函数，根据环境变量选择上传到OSS或TOS
    
    Args:
        image_path: 本地图片路径
    
    Returns:
        str: 图片的公开访问URL
        
    Raises:
        Exception: 上传失败时抛出异常
    """
    model_flow = os.environ.get("ENV_MODEL_FLOW", "").lower()
    
    try:
        if model_flow == "ark":
            from ctn2md.utils_llm.llm_base_tos import upload_image_to_tos
            logging.info(f"Using TOS for upload: {image_path}")
            return upload_image_to_tos(image_path)
        else:
            from ctn2md.utils_llm.llm_base_oss import upload_image_to_oss
            logging.info(f"Using OSS for upload: {image_path}")
            return upload_image_to_oss(image_path)
    except Exception as e:
        logging.error(f"Upload failed for {image_path}: {str(e)}")
        raise

def get_gpt_messages_multimodal(system_prompt:str, user_prompt:str, image_path_or_url:str) -> list:
    """生成支持多模态的消息结构"""
    # 如果已经是远程URL，直接使用
    if image_path_or_url.startswith(('http://', 'https://')):
        img_url = image_path_or_url
    else:
        # 本地文件需要上传到OSS
        img_url = upload_image_to_cloud(image_path_or_url)
    
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

def wait_random_exponential_with_rate_limit(multiplier=1, min_seconds=4, max_seconds=60):
    """自定义等待策略，对 RateLimitError 使用更长的等待时间"""
    def wait_handler(retry_state):
        # 获取最后一次异常
        exc = retry_state.outcome.exception()
        
        # 基础等待时间
        wait_time = wait_exponential(
            multiplier=multiplier, 
            min=min_seconds, 
            max=max_seconds
        ).__call__(retry_state)
        
        # 如果是 RateLimitError，显著增加等待时间
        if isinstance(exc, openai.RateLimitError):
            wait_time = min(wait_time * 3, 300)  # 最多等待5分钟
            logging.warning(f"Rate limit exceeded, increasing wait time to {wait_time} seconds")
        
        return wait_time
    return wait_handler

@retry(
    stop=stop_after_attempt(DEFAULT_RETRY_NUM),
    wait=wait_random_exponential_with_rate_limit(multiplier=1, min_seconds=4, max_seconds=60),
    retry=retry_if_exception_type((httpx.RequestError, ValueError, openai.RateLimitError)),
    before_sleep=lambda retry_state: logging.info(f"Retrying after {retry_state.next_action.sleep} seconds...")
)
def chat_gpt_json(
    messages: List[Dict[str, str]], 
    model: str = "gpt-4o-mini", 
    temperature: float = 0.1, 
    top_p: float = 0.9,
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
    
    try:
        with MonitorContextLLM(messages, model, track_id, 0) as mc:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                response_format={"type": "json_object"})
            mc.response = response
            resp = jsons_load_repair(response.choices[0].message.content)
            return resp
    except openai.BadRequestError as e:
        logging.exception(e)
        raise

@retry(
    stop=stop_after_attempt(DEFAULT_RETRY_NUM),
    wait=wait_random_exponential_with_rate_limit(multiplier=1, min_seconds=4, max_seconds=60),
    retry=retry_if_exception_type((httpx.RequestError, ValueError, openai.RateLimitError)),
    before_sleep=lambda retry_state: logging.info(f"Retrying after {retry_state.next_action.sleep} seconds...")
)
def chat_gpt_plain(
    messages: list,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    top_p: float = 0.9,
    track_id: Optional[str] = None,
    client: Optional[OpenAI] = None
) -> str:
    if client is None:
        client = get_azure_gpt_client()
    
    try:
        with MonitorContextLLM(messages, model, track_id, 0) as mc:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p)
            mc.response = response
            return response.choices[0].message.content
    except openai.BadRequestError as e:
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