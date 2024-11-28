import dashscope
import time
import random
import os
import logging
import sys
#import json
import rich
from dotenv import load_dotenv

#import json_repair


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_llm.vllm_ocr_restore_prompt import PROMPT_INSTRUCT_OCR_QWEN_START, PROMPT_INSTRUCT_OCR_QWEN_CONTINUE
from ctn2md.utils_llm.vllm_ocr_restore_prompt import PROMPT_INSTRUCT_OCR_QWEN_SINGLE

dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]


def _retry_dashscope_get_response(messages, retries=5, backoff_in_seconds=1):
    for attempt in range(retries):
        try:
            response = dashscope.MultiModalConversation.call(
                model='qwen-vl-max-0809', 
                messages=messages, 
                top_p=0.1,
                max_length=2000)
            return response 
        except Exception as e:
            logging.exception(e)
            if attempt == retries - 1:
                raise
            sleep_time = backoff_in_seconds * (2**attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)


def generate_long_mds_from_image(image_url, doc_title=None, retries=5, backoff_in_seconds=1):
         
    messages = [{'role': 'user',
                 'content': [{'image': image_url}, {'text': PROMPT_INSTRUCT_OCR_QWEN_START}]}]
    
    # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.
    logging.info(f"GLMFI: generate_long_mds_from_image started... {image_url}")
    full_content = ""
    for loop in range(4):
        logging.info(f"GLMFI: start loop:{loop}")
        response =_retry_dashscope_get_response(messages, retries=retries, backoff_in_seconds=backoff_in_seconds)
        content = response.output.choices[0].message.content
        text_content = content[0]["text"]
        text_content = text_content.replace("```markdown", "") 
        full_content += text_content
        if text_content.find("[ocr_end]") != -1:
            logging.info(f"GLMFI: finished [ocr_end] loop@{loop}")
            break
        if response.output.finish_reason:
            logging.info(f"GLMFI: finished finish_reason @{loop}")
            break
        if len(messages) == 1:
            messages.append(
                {'role': response.output.choices[0].message.role,
                 'content': [{'text': text_content}]})
            messages.append(
                {'role': 'user',
                 'content':[{'text': PROMPT_INSTRUCT_OCR_QWEN_CONTINUE}]})
        else:
            messages[1]["content"] = [{'text': full_content}]
    full_content = full_content.replace("[ocr_end]", "")
    #rich.print(messages)
    logging.info(f"GLMFI: total output length {len(full_content)}")
    logging.info(f"GLMFI: generate_long_mds_from_image ended. {image_url}")
    return full_content

def generate_simple_mds_from_image(image_url, doc_title=None, retries=5, backoff_in_seconds=1):
         
    messages = [{'role': 'user',
                 'content': [{'image': image_url}, {'text': PROMPT_INSTRUCT_OCR_QWEN_SINGLE}]}]
    
    # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.

    logging.info(f"GSMFI: generate_simple_mds_from_image started... {image_url}")
    response =_retry_dashscope_get_response(messages, retries=retries, backoff_in_seconds=backoff_in_seconds)
    content = response.output.choices[0].message.content
    text_content = content[0]["text"]
    full_content = text_content.replace("```markdown", "") 
    logging.info(f"GSMFI: total output length {len(full_content)}")
    logging.info(f"GSMFI: generate_simple_mds_from_image ended. {image_url}")

    return full_content

if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #image_url = "_work/md_samples/ed2f9c59-b65b-422c-a76e-03961eabc326-img_p0_1.png"
    #image_url = "_work/md_samples/ed2f9c59-b65b-422c-a76e-03961eabc326-img_p1_1.png"
    #image_url = "_work/md_samples/5a358191-8ca2-46e1-8c08-b574f947c1aa-img_p0_1.png"
    #image_url = "_work/md_samples/5a358191-8ca2-46e1-8c08-b574f947c1aa-img_p1_1.png"
    #image_url = "_work/md_samples/0b4a463c-d485-4a89-8eef-1d903ef68b70-page_5.jpg"
    #image_url = "_work/md_samples/45bef982-6228-4314-9c69-1f24a0c36931-page_6.jpg"
    image_url = "_work/md_samples/0b4a463c-d485-4a89-8eef-1d903ef68b70-page_15.jpg"

    full_path = os.path.join(dir_root, image_url)
    container_name = os.path.basename(os.path.dirname(image_url))

    #text = generate_long_mds_from_image(full_path)
    #rich.print(text)

    text = generate_simple_mds_from_image(full_path)
    rich.print(text)
