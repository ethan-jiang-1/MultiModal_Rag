import dashscope
import time
import random
import os
import logging
import sys
#import json
#import rich
import csv
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]

g_monitor_filename = None 
def _get_monitor_qwen_mm_filename():
    global g_monitor_filename
    if g_monitor_filename is None:
        dir_root = os.path.dirname(find_dotenv())
        dir_logs = os.path.join(dir_root, "logs")
        os.makedirs(dir_logs, exist_ok=True)
        filename = os.path.join(dir_logs, "ctn_qwen_mm_monitor.csv")
        g_monitor_filename = filename
    return g_monitor_filename

def _monitor_qwen_mm_call(d0, messages, response, model, track_id=None):
    d1 = time.time()

    try:
        filename = _get_monitor_qwen_mm_filename()

        # d0 = response.created
        dt = d1 - d0
        dt = round(dt, 2)
        d0 = round(d0, 2)

        ts0 = datetime.fromtimestamp(d0).strftime("%Y%m%d:%H:%M:%S")

        output = response.output
        choice0 = output.choices[0]
        finish_reason = choice0.finish_reason

        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        image_tokens = usage.image_tokens

        sec_span = round(dt, 2)
        output_ratio_per_sec = round(float(output_tokens) / sec_span, 2)
        token_per_ms = round((1.0/output_ratio_per_sec) * 1000.0, 2)

        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ts0, finish_reason, model, sec_span, input_tokens, image_tokens, output_tokens, token_per_ms, str(track_id)])

    except Exception as ex:  # noqa
        print(ex)



def call_mmc_qwen(messages, model='qwen-vl-max-1119', retries=5, backoff_in_seconds=1, track_id=None):
    for attempt in range(retries):
        try:
            d0 = time.time()
            response = dashscope.MultiModalConversation.call(
                model=model, 
                messages=messages)
            _monitor_qwen_mm_call(d0, messages, response, model, track_id=track_id)
            return response
        except Exception as e:
            logging.exception(e)
            if attempt == retries - 1:
                raise
            sleep_time = backoff_in_seconds * (2**attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
    return None