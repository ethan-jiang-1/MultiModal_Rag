from dotenv import load_dotenv, find_dotenv
import os
import logging
import time
import csv
from datetime import datetime

load_dotenv()


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
        self.d1 = time.time()
        logging.info(f"MonitorContextLLM exit model:{self.model}")
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