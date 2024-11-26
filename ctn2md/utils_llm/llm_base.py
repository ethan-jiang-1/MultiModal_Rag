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
import datetime
import rich 
#import json

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

"""
| Task            | `temperature`  | `top_p`       | Comment                                                              |
|-----------------|----------------|---------------|----------------------------------------------------------------------|
| SQL Generation  | `0.0` - `0.2`  | `0.9` - `1.0` | Prioritizes precision and correctness in SQL generation.             |
| Analysis        | `0.3` - `0.6`  | `0.85` - `1.0`| Balances logic with some creativity for diverse perspectives.        |
| Report          | `0.5` - `0.7`  | `0.9` - `1.0` | Supports natural, varied language for detailed report writing.       |

"""

DEFAULT_RETRY_NUM = 5

def get_gpt_messages(system_prompt, user_prompt):
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
    #messages_str = json.dumps(messages)
    #messages_loaded = json.loads(messages_str)
    return messages

def get_azure_gpt_client():
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    return client

def get_dashscope_client():
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return client


def jsons_load_repair(content):
    resp = json_repair.repair_json(content, 
                                   ensure_ascii=True, 
                                   return_objects=True)
    return resp

g_monitor_filename = None 
def _get_monitor_filename():
    global g_monitor_filename
    if g_monitor_filename is None:
        dir_root = os.path.dirname(find_dotenv())
        dir_logs = os.path.join(dir_root, "logs")
        os.makedirs(dir_logs, exist_ok=True)
        filename = os.path.join(dir_logs, "ctn_monitor.csv")
        g_monitor_filename = filename
    return g_monitor_filename

def _monitor_call(d0, messages, response, track_id=None):
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

        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ts0, finish_reason, model, sec_span, total_tokens, prompt_tokens, completion_tokens, token_per_ms, str(track_id)])

    except:  # noqa
        pass 


def chat_gpt_json(messages, 
                  model="gpt-4o-mini", 
                  temperature=0.1, 
                  top_p=0.9,
                  retries=DEFAULT_RETRY_NUM,
                  backoff_factor=2,
                  backoff_sec=1,
                  delay_base_sec=5,
                  track_id=None,
                  client=None):
    attempt = 0
    if client is None:
        client = get_azure_gpt_client()
    while attempt < retries:
        try:
            d0 = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                response_format={"type": "json_object"})
            _monitor_call(d0, messages, response, track_id=track_id)
            resp = jsons_load_repair(response.choices[0].message.content)
            return resp
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logging.error(f"Error on attempt {attempt+1}: {str(e)}")
            attempt += 1
            if attempt == retries:
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logging.info(f"Retrying after backoff: {backoff_sec} seconds...")
            time.sleep(backoff_sec)

def chat_gpt_plain(messages, 
                  model="gpt-4o-mini", 
                  temperature=0.1, 
                  top_p=0.9,
                  retries=DEFAULT_RETRY_NUM,
                  backoff_factor=2,
                  backoff_sec=1,
                  delay_base_sec=5,
                  track_id=None,
                  client=None):
    attempt = 0
    if client is None:
        client = get_azure_gpt_client()
    while attempt < retries:
        try:
            d0 = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p)
            _monitor_call(d0, messages, response, track_id=track_id)
            return response.choices[0].message.content
        except (requests.exceptions.RequestException, ValueError, openai.RateLimitError) as e:
            if isinstance(e, openai.RateLimitError):
                delay_base_sec += 10
            else:
                logging.error(f"Error on attempt {attempt+1}: {str(e)}")
            attempt += 1
            if attempt == retries:
                raise
            backoff_sec = backoff_factor**attempt + delay_base_sec
            logging.info(f"Retrying after backoff: {backoff_sec} seconds...")
            time.sleep(backoff_sec)


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