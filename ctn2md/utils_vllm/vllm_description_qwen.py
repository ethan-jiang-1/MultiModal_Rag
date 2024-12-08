import dashscope
import time
import random
import os
import logging
import sys
#import json
import rich
from dotenv import load_dotenv



if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_vllm.vllm_description_qwen_prompt import PROMPT_QUESTION_QAGEN_QWEN

dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]

#model='qwen-vl-max-1119'
#model='qwen-vl-max-0809'
def generate_image_description_by_qwen(image_url, instruction=None, model='qwen-vl-max-1119', retries=5, backoff_in_seconds=1):

    if instruction is None:
        instruction = "请简单描述一下这张图片。"
         
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
    # 
    for attempt in range(retries):
        try:
            response = dashscope.MultiModalConversation.call(
                model=model, 
                messages=messages)
            if response is not None: 
                choice = response["output"]["choices"][0]
                content = choice["message"]["content"]
                answer_text = content[0]["text"]
                return answer_text
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

    image_url = "datasets/test/images/头枕杆圆角定义/头枕杆圆角定义_img_P10.png"

    full_path = os.path.join(dir_root, image_url)
    container_name = os.path.basename(os.path.dirname(image_url))

    # ret1 = generate_image_description_by_qwen(full_path)
    # print(ret1)
    # print()

    #instruction = f"这是一张在'{container_name}'文件中的图片， 请简单描述一下这张图片。"   
    #ret2 = generate_image_description_by_qwen(full_path, instruction=instruction)
    #print(ret2)
    #print()

    instruction = f"这是一张在'{container_name}'文件中的图片， 请详细描述一下这张图片。 要被用到知识库建设中，所以知识性细节越多越好."   
    ret3 = generate_image_description_by_qwen(full_path, instruction=instruction)
    rich.print(ret3)
    print()

    instruction = PROMPT_QUESTION_QAGEN_QWEN.replace("{container_name}", container_name)
    ret4 = generate_image_description_by_qwen(full_path, instruction=instruction)
    rich.print(ret4)
    print()