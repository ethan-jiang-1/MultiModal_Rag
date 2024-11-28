import dashscope
import time
import random
import os
import logging
import sys
#import json
import rich
from dotenv import load_dotenv

import json_repair


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_llm.vllm_ocr_restore_prompt import PROMPT_INSTRUCT_OCR_QWEN

dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]


def generate_mds_from_image(image_url, doc_title=None, retries=5, backoff_in_seconds=1):

    instruction = PROMPT_INSTRUCT_OCR_QWEN
         
    messages = [{
        'role': 'user',
        'content': [
            {
                'image': image_url
            },
            {
                'text': instruction
            },
        ]
    }]
    
    # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.
    for attempt in range(retries):
        try:
            response = dashscope.MultiModalConversation.call(
                model='qwen-vl-max-0809', 
                messages=messages, 
                top_p=0.1)
            choice = response["output"]["choices"][0]
            content = choice["message"]["content"][0]["text"]
            return json_repair.repair_json(content, return_objects=True)
        except Exception as e:
            logging.exception(e)
            if attempt == retries - 1:
                raise
            sleep_time = backoff_in_seconds * (2**attempt) + random.uniform(
                0, 1)
            time.sleep(sleep_time)
    return None

if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    image_url = "_work/md_samples/ed2f9c59-b65b-422c-a76e-03961eabc326-img_p0_1.png"
    #image_url = "_work/md_samples/ed2f9c59-b65b-422c-a76e-03961eabc326-img_p1_1.png"
    #image_url = "_work/md_samples/5a358191-8ca2-46e1-8c08-b574f947c1aa-img_p0_1.png"
    #image_url = "_work/md_samples/5a358191-8ca2-46e1-8c08-b574f947c1aa-img_p1_1.png"

    full_path = os.path.join(dir_root, image_url)
    container_name = os.path.basename(os.path.dirname(image_url))

    resp = generate_mds_from_image(full_path)
    rich.print(resp)
    print(resp["markdown"])

