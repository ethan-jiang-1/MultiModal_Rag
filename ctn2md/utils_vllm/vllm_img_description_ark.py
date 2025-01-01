import os
import sys
from typing import Optional
import rich
from dotenv import load_dotenv


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_llm.llm_base import get_gpt_messages_multimodal, chat_gpt_plain, get_ark_client
from ctn2md.utils.util_file import get_root_dir
from ctn2md.utils_vllm.vllm_img_description_ark_prompt import TEXT_IMG_DESCRIPTION

def generate_image_description_by_ark(image_path_or_url:str, 
                                      instruction:Optional[str] = None, 
                                      model:str = "ep-20241220100411-qb77p", 
                                      retries:int = 5, 
                                      backoff_in_seconds:int = 1) -> str:

    if instruction is None:
        instruction = TEXT_IMG_DESCRIPTION

    if not image_path_or_url.startswith(('http://', 'https://')):
        if not os.path.isfile(image_path_or_url):
            raise ValueError(f"Local file {image_path_or_url} does not exist")

    messages = get_gpt_messages_multimodal(None, instruction, image_path_or_url)
    client = get_ark_client()
    response = chat_gpt_plain(messages, client=client, model=model)
    return response

def test_gen_qas_on_pic():
    image_path = "_work/md_pdf_pages/5ec48698-page_1.jpg"

    full_path = os.path.join(dir_root, image_path)
    container_name = os.path.basename(os.path.dirname(image_path))

    instruction = None
    ret2 = generate_image_description_by_ark(full_path, instruction=instruction)
    rich.print(ret2)
    print()

    instruction = f"这是一张在'{container_name}'文件中的图片， 请详细描述一下这张图片。 要被用到知识库建设中，所以知识性细节越多越好."   
    ret3 = generate_image_description_by_ark(full_path, instruction=instruction)
    rich.print(ret3)
    print()

    instruction = TEXT_PROMPT_INST_VLLM_GEN_QAS.replace("{container_name}", container_name)
    ret4 = generate_image_description_by_ark(full_path, instruction=instruction)
    rich.print(ret4)
    print()

if __name__ == '__main__':
    from ctn2md.utils.util_logging import setup_logger_handlers
    from ctn2md.utils_vllm.vllm_img_description_gpt_prompt import TEXT_PROMPT_INST_VLLM_GEN_QAS

    dir_root = get_root_dir()
    setup_logger_handlers()

    image_path = "_work/md_pdf_pages/5ec48698-page_1.jpg"

    full_path = os.path.join(dir_root, image_path)
    container_name = os.path.basename(os.path.dirname(image_path))

    ret1 = generate_image_description_by_ark(full_path)
    print(ret1)
    print()
    print("-----")

    instruction = f"这是一张在'{container_name}'文件中的图片， 要被用到知识库建设中，所以知识性细节越多越好，但所有内容**一定要保持在一个段落**里面, 请用完整的**一个段落**, 详细描述一下这张图片。 ." 
    ret2 = generate_image_description_by_ark(full_path, instruction=instruction)
    print(ret2)
    print()

