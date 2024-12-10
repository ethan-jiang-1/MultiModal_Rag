#import time
#import random
import os
import logging
import sys
#import json
import rich
import json_repair
from dotenv import load_dotenv

#import json_repair


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_vllm.vllm_img2region_qwen_prompt import PROMPT_INSTRUCT_IMG2REGION_QWEN
from ctn2md.utils_vllm.vllm_base import chat_qwen_mm

def generate_regions_from_image_qwen(pname_image, model='qwen-vl-max-1119', retries=5, backoff_in_seconds=1):
    
    prompt = PROMPT_INSTRUCT_IMG2REGION_QWEN

    messages = [{'role': 'user',
                 'content': [{'image': pname_image}, {'text': prompt}]}]
    
    # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.
    logging.info(f"GFMFI: generate_regions_from_image_qwen started... {pname_image}")

    response = chat_qwen_mm(messages, model=model, retries=retries, backoff_in_seconds=backoff_in_seconds, track_id="gfmdiq")

    resp = json_repair.repair_json(response, return_objects=True)
    logging.info(f"GFMFI: generate_regions_from_image_qwen ended. {pname_image}")
    return resp


if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']
    #rects_img = None

    pname_image = "_work/md_pdf_pages/c3c1d78a-page_3_rects.jpg"

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    resp = generate_regions_from_image_qwen(full_path)
    rich.print(resp)
