import dashscope
import time
import random
import os
import logging
import sys
#import json
import rich
from dotenv import load_dotenv
from openai import AzureOpenAI
import json_repair


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from HiQA.utils.util_file import get_root_dir
from HiQA.build_tool.vl_description_prompt import PROMPT_QUESTION_QAGEN_QWEN, SYSTEM_PROMPT_GPT4_QAGEN, USER_PROMPT_GPT4_QAGEN
from HiQA.utils.util_logging import setup_logger_handlers

dashscope.api_key = "sk-a7cb64d9e5124609ac52849950c6fee2"


def _get_gpt_messages(prompt):
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT_GPT4_QAGEN
        },
        {
            "role": "user",
            "content": prompt
        },
    ]
    return messages

def gen_questions_on_pic_by_gpt4(container_name, img_desc):
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    try:
        logging.info("start to generate questions...")
        prompt = USER_PROMPT_GPT4_QAGEN.replace("{container_name}", container_name).replace("{img_desc}", img_desc)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=_get_gpt_messages(prompt),
            temperature=0.3,
            top_p=0.95)
        response_content = response.choices[0].message.content
        res = json_repair.repair_json(response_content, ensure_ascii=True, return_objects=True)
        return res
    except Exception as ex: 
        logging.exception(ex)
        raise ex


def generate_image_description(image_url, instruction=None, retries=5, backoff_in_seconds=1):

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
    for attempt in range(retries):
        try:
            response = dashscope.MultiModalConversation.call(
                model='qwen-vl-max-0809', messages=messages)
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


if __name__ == '__main__':
    dir_root = get_root_dir()
    setup_logger_handlers()

    image_url = "datasets/test/images/头枕杆圆角定义/头枕杆圆角定义_img_P10.png"

    full_path = os.path.join(dir_root, image_url)
    container_name = os.path.basename(os.path.dirname(image_url))

    # ret1 = generate_image_description(full_path)
    # print(ret1)
    # print()

    #instruction = f"这是一张在'{container_name}'文件中的图片， 请简单描述一下这张图片。"   
    #ret2 = generate_image_description(full_path, instruction=instruction)
    #print(ret2)
    #print()

    instruction = f"这是一张在'{container_name}'文件中的图片， 请详细描述一下这张图片。 要被用到知识库建设中，所以知识性细节越多越好."   
    ret3 = generate_image_description(full_path, instruction=instruction)
    print(ret3)
    print()

    instruction = PROMPT_QUESTION_QAGEN_QWEN.replace("{container_name}", container_name)
    ret4 = generate_image_description(full_path, instruction=instruction)
    print(ret4)
    print()

    img_desc = ret3
    ret5 = gen_questions_on_pic_by_gpt4(container_name, img_desc)
    rich.print(ret5)
    print()