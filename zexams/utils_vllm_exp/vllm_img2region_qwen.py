import os
import logging
import rich
import json_repair
from dotenv import load_dotenv

load_dotenv()

from ctn2md.utils_vllm_exp.vllm_img2region_qwen_prompt import PROMPT_INSTRUCT_IMG2REGION_QWEN
from mmbase.utils_llm.llm_base import get_dashscope_client, get_gpt_messages_multimodal, chat_gpt_plain


def generate_regions_from_image_qwen(pname_image:str, 
                                     model:str = 'qwen-vl-max-1119') -> dict:
    
    prompt = PROMPT_INSTRUCT_IMG2REGION_QWEN
    if not os.path.isfile(pname_image):
        raise ValueError(f"file {pname_image} not exit")

    messages = get_gpt_messages_multimodal(None, prompt, pname_image)

    client = get_dashscope_client()

    logging.info(f"GRFIQ: convert pdf page {pname_image} to regions by gpt started...")
    resp_str = chat_gpt_plain(messages, model=model, client=client, temperature=0.01, top_p=0.95)    
    return json_repair.repair_json(resp_str, return_objects=True)


if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from mmbase.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']
    #rects_img = None

    #pname_image = "_work/md_pdf_pages/c3c1d78a-page_3_rects.jpg"
    pname_image = "_work/md_pdf_pages/bd72132b-page_3.jpg"
    #pname_image = "_work/md_pdf_pages/bd72132b-page_4.jpg"

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    resp = generate_regions_from_image_qwen(full_path)
    rich.print(resp)
