import sys
import time
import json
import requests
import logging
import random
import rich
import os
import csv
import datetime
import openai
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI

if './' not in sys.path:
    sys.path.append("./")
load_dotenv()

from HiQA.utils.util_logging import setup_logger_handlers

endpoint = os.environ['AZURE_OPENAI_ENDPOINT']
api_key = os.environ['AZURE_OPENAI_API_KEY']

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=os.environ["AZURE_OPENAI_VERSION"]
)

"""
| Task            | `temperature`  | `top_p`       | Comment                                                              |
|-----------------|----------------|---------------|----------------------------------------------------------------------|
| SQL Generation  | `0.0` - `0.2`  | `0.9` - `1.0` | Prioritizes precision and correctness in SQL generation.             |
| Analysis        | `0.3` - `0.6`  | `0.85` - `1.0`| Balances logic with some creativity for diverse perspectives.        |
| Report          | `0.5` - `0.7`  | `0.9` - `1.0` | Supports natural, varied language for detailed report writing.       |

"""

setup_logger_handlers()
logger = logging.getLogger(__name__)
logger_llm = logger

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

DEFAULT_CHAT_TIMEOUT = 2.0 * 60 # 2min

DEFAULT_RETRY_NUM = 10

ENV_MODEL_GPT_MODE = "ENV_MODEL_GPT_MODE"

class ModelSelector:
    MODEL_GPT4O = "gpt-4o"
    MODEL_GPT4O_MINI = "gpt-4o-mini"

    GMM_DEFAULT = "default"
    GMM_FAST = "fast"
    GMM_SMART = "smart"

    @classmethod
    def get_model_fast(cls):
        return cls.MODEL_GPT4O_MINI

    @classmethod
    def get_model_smart(cls):
        gmm = cls.get_gpt_model_mode()
        if gmm == cls.GMM_FAST:
            return cls.MODEL_GPT4O_MINI
        return cls.MODEL_GPT4O

    @classmethod
    def get_model_normal(cls):
        gmm = cls.get_gpt_model_mode()
        if gmm == cls.GMM_FAST:
            return cls.MODEL_GPT4O_MINI
        return cls.MODEL_GPT4O

    @classmethod
    def get_gpt_model_mode(cls):
        gmm = os.environ.get(ENV_MODEL_GPT_MODE, cls.GMM_DEFAULT)
        gmm = gmm.lower().strip()
        return gmm

    @classmethod
    def get_gpt_model_list(cls):
        return [cls.get_model_fast(), cls.get_model_normal(), cls.get_model_smart()]

    @classmethod
    def set_gpt_model_mode(cls, gmm_value):
        gmm_value = gmm_value.lower()
        if gmm_value in [cls.GMM_DEFAULT, cls.GMM_SMART, cls.GMM_FAST]:
            os.environ[ENV_MODEL_GPT_MODE] = gmm_value
            msg = f"ENV_MODEL_GPT_MODE set to {gmm_value}"
            print(msg)
            logging.info(msg)

g_monitor_filename = None 
def _get_monitor_filename():
    global g_monitor_filename
    if g_monitor_filename is None:
        dir_root = os.path.dirname(find_dotenv())
        dir_logs = os.path.join(dir_root, "logs")
        os.makedirs(dir_logs, exist_ok=True)
        filename = os.path.join(dir_logs, "llm_monitor.csv")
        g_monitor_filename = filename
    return g_monitor_filename

def _get_question_num_str():
    question_num = 0
    try:
        from text2sql.util.util_files import get_exam_question_num
        question_num = get_exam_question_num()
    except: # noqa
        pass
    if isinstance(question_num, int):
        return "{:03}".format(question_num)
    return "000"

def _monitor_call(d0, cc_id, messages, response, track_id):
    d1 = time.time()

    try:
        filename = _get_monitor_filename()

        # d0 = response.created
        dt = d1 - d0
        dt = round(dt, 2)
        d0 = round(d0, 2)

        ts0 = datetime.datetime.fromtimestamp(d0).strftime("%Y%m%d:%H:%M:%S")

        choice0 = response.choices[0]
        finish_reason = choice0.finish_reason

        model = response.model

        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        total_tokens = usage.total_tokens
        completion_tokens = usage.completion_tokens

        sec_span = round(dt, 2)
        output_ratio_per_sec = round(float(completion_tokens) / sec_span, 2)
        token_per_ms = round((1.0/output_ratio_per_sec) * 1000.0, 2)

        qnum = _get_question_num_str()

        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ts0, qnum, cc_id, finish_reason, model, sec_span, total_tokens, prompt_tokens, completion_tokens, token_per_ms, track_id])

    except:  # noqa
        pass 

def get_gpt_messages(system_prompt, user_prompt):
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        },
    ]
    return messages


def chat_completions(prompt,
                     system_prompt=DEFAULT_SYSTEM_PROMPT,
                     messages=None,
                     top_p=0.1,
                     temperature=0.2,
                     retries=DEFAULT_RETRY_NUM,
                     backoff_factor=2,
                     model=ModelSelector.MODEL_GPT4O,
                     timeout=DEFAULT_CHAT_TIMEOUT,
                     track_id=None):
    attempt = 0
    delay_base_sec = 1
    cc_id = f"cc_id:{random.randint(10000, 99999)}"
    logger_llm.info(f"{cc_id}")
    while attempt < retries:
        try:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ] if messages is None else messages
            logger.info(f"make llm call: {cc_id} started...")
            logger_llm.info(f"{cc_id} Attempt {attempt+1}: Sending chat completion:\n {messages}")
            d0 = time.time()
            response = client.chat.completions.create(
                model=model,
                # model= "deepseek-ai/DeepSeek-Coder-V2-Instruct",
                messages=messages,
                top_p=top_p,
                temperature=temperature,
                timeout=timeout)
            _monitor_call(d0, cc_id, messages, response, track_id)
            logger.info(f"make llm call: {cc_id} ended.")
            logger_llm.info(f"{cc_id} Attempt {attempt+1}: response:\n {response}")
            response_content = response.choices[0].message.content
            if response_content:
                logger_llm.info(f"Received response: {response_content}")
                return response_content
            else:
                raise ValueError("Response content is None")
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logger.error(f"Error on attempt {attempt+1}: {str(e)}",
                            exc_info=True)
            logger_llm.exception(f"{cc_id} Exception: {str(e)}")
            attempt += 1
            if attempt == retries:
                logger.error(
                    f"Max retries reached. Failed to get valid response after {retries} attempts."
                )
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logger.info(
                f"{cc_id} Retrying after backoff: {backoff_sec} seconds..."
            )
            time.sleep(backoff_sec)
 
    logger_llm.error(f"{cc_id} Failed to get valid response after retries:{retries}")
    return None


def is_valid_json(response_json_string):
    try:
        json.loads(response_json_string)
        return True
    except ValueError:
        return False


def is_fixable_json(response_json_string):
    try:
        ret = json_loads_repair(response_json_string)
        return ret
    except Exception as ex:
        logging.exception(str(ex))
    return None


def json_loads_repair(response_json_string):
    if is_valid_json(response_json_string):
        return json.loads(response_json_string)
    else:
        logging.warning(f"try to repair json: {response_json_string}")
        import json_repair
        ret = json_repair.repair_json(response_json_string, return_objects=True)
        return ret


def chat_completions_response_json(prompt,
                                   system_prompt=DEFAULT_SYSTEM_PROMPT,
                                   messages=None,
                                   top_p=0.1,
                                   temperature=0.2,
                                   retries=DEFAULT_RETRY_NUM,
                                   backoff_factor=2,
                                   model=ModelSelector.MODEL_GPT4O,
                                   enforced_fix_json=True, 
                                   timeout=DEFAULT_CHAT_TIMEOUT,
                                   track_id=None,
                                   max_tokens=None):
    attempt = 0
    delay_base_sec = 1
    cc_id = f"cj_id:{random.randint(10000, 99999)}"
    logger_llm.info(f"{cc_id}")
    while attempt < retries:
        try:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ] if messages is None else messages

            logger.info(f"make llm call: {cc_id} started...")
            logger_llm.info(f"{cc_id} Attempt {attempt+1}: Sending chat completion:\n {messages}")
            d0 = time.time()
            if isinstance(max_tokens, int):
                response = client.chat.completions.create(
                    model=model,
                    # model= "deepseek-ai/DeepSeek-Coder-V2-Instruct",
                    messages=messages,
                    top_p=top_p,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    timeout=timeout,
                    max_tokens=max_tokens)
            else:
                response = client.chat.completions.create(
                    model=model,
                    # model= "deepseek-ai/DeepSeek-Coder-V2-Instruct",
                    messages=messages,
                    top_p=top_p,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    timeout=timeout)                
            _monitor_call(d0, cc_id, messages, response, track_id)
            logger.info(f"make llm call: {cc_id} ended.")
            logger_llm.info(f"{cc_id} Attempt {attempt+1}: response:\n {response}")
            response_content = response.choices[0].message.content
            if is_valid_json(response_content):
                # logger.info(f"Received valid JSON response: {response_content}")
                return response_content
            elif enforced_fix_json:
                logging.warning(f"content is not json format, try to fix: {response_content}")
                if is_fixable_json(response_content):
                    return response_content
            logging.error(f"{cc_id} Response is not valid json: {response_content}")
            raise ValueError("Response is not a valid JSON")
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logger.error(f"{cc_id} Error on attempt {attempt+1}: {str(e)}",
                            exc_info=True)
            logger_llm.exception(f"{cc_id} Exception: {str(e)}")
            attempt += 1
            if attempt == retries:
                logger.error(
                    f"{cc_id} Max retries reached. Failed to get valid JSON response after {retries} attempts."
                )
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logger.info(
                f"{cc_id} Retrying after backoff: {backoff_sec} seconds..."
            )
            time.sleep(backoff_sec)
    
    logger_llm.error(f"{cc_id} Failed to get valid response after retries:{retries}")
    return None

if __name__ == "__main__":
    prompt = "hi, who are you? tell me your model name, response in json"
    response = chat_completions_response_json(prompt,
                                              track_id="t1")
    response_dict = json_loads_repair(response)
    rich.print(response_dict)

    response = chat_completions_response_json(prompt,
                                              model=ModelSelector.get_model_fast(),
                                              track_id="t2")
    response_dict = json_loads_repair(response)
    rich.print(response_dict)