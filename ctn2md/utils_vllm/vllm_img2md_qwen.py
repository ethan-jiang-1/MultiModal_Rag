import os
import logging
from typing import List
import rich
from dotenv import load_dotenv

load_dotenv()

from ctn2md.utils_vllm.vllm_img2md_qwen_prompt import PROMPT_INSTRUCT_IMG2MD_QWEN, PROMPT_INSTRUCT_IMG2MD_QWEN_IMG_RECTS
from mmbase.utils_llm.llm_base import get_dashscope_client, get_gpt_messages_multimodal, chat_gpt_plain
from mmbase.utils_llm.llm_markdown import strip_llm_format_markers

def generate_full_mds_from_image_qwen(pname_image:str, 
                                      rects_img:List[str] = None, 
                                      model:str = 'qwen-vl-max-1119', 
                                      retries:int = 5, 
                                      backoff_in_seconds:int = 1)->str:
         
    inst_img_rects = ""
    if rects_img is not None and len(rects_img) > 0:
        rects_img = sorted(rects_img)
        img_rects = ""
        for ndx, rect_img in enumerate(rects_img):
            img_rects += f" `red_rect{ndx+1}`: {rect_img}, "
        inst_img_rects = PROMPT_INSTRUCT_IMG2MD_QWEN_IMG_RECTS.replace("{img_rects}", img_rects)
    
    prompt_start = PROMPT_INSTRUCT_IMG2MD_QWEN.replace("{inst_img_rects}", inst_img_rects)

    messages = get_gpt_messages_multimodal(None, prompt_start, pname_image)

    client = get_dashscope_client()

    logging.info(f"GFMFI: generate_full_mds_from_image started... {pname_image}")
    resp_str = chat_gpt_plain(messages, model=model, client=client, temperature=0.01, top_p=0.95)    
    
    resp_str = strip_llm_format_markers(resp_str)
    
    #rich.print(resp_str)
    return resp_str


if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from mmbase.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']

    # pname_image = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
    # rects_img = ['5ec48698-img_1_4.jpg',
    #              '5ec48698-img_1_3.jpg',
    #              '5ec48698-img_1_2.jpg',
    #              '5ec48698-img_1_1.jpg']
    
    #pname_image = "_work/md_pdf_pages/d73162ba-page_2_rects.jpg"
    #rects_img = []

    pname_image = "_work/md_pdf_pages/d73162ba-page_3_rects.jpg"
    rects_img = []

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    text = generate_full_mds_from_image_qwen(full_path, rects_img=rects_img)
    rich.print(text)
