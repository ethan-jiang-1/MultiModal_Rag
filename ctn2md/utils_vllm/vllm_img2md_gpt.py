from typing import List, Optional
from dotenv import load_dotenv
import os
import logging
import rich

load_dotenv()

from mmbase.utils_llm.llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from mmbase.utils_llm.llm_base import get_gpt_messages_multimodal, chat_gpt_plain
from mmbase.utils_llm.llm_markdown import strip_llm_format_markers
from ctn2md.utils_vllm.vllm_img2md_gpt_prompt import SYSTEM_PROMPT_IMG2MD, USER_PROMPT_IMG2MD, USER_PROMPT_INST_IMG_RECTS


def generate_full_mds_from_image_gpt(pname_image:str, 
                                     rects_img:List[str] = None, 
                                     model:str = "gpt-4o", 
                                     question_num:Optional[int] = None) -> str:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if model not in ["gpt-4o"]: 
            raise ValueError(f"f{model} not supported")
        system_prompt = SYSTEM_PROMPT_IMG2MD

        inst_img_rects = ""

        if rects_img is not None and len(rects_img) > 0:
            rects_img = sorted(rects_img)
            img_rects = ""
            for ndx, rect_img in enumerate(rects_img):
                if len(inst_img_rects) != 0:
                    img_rects += "\n"
                img_rects += f"- `red_rect{ndx+1}`: {rect_img}\n"

            inst_img_rects = USER_PROMPT_INST_IMG_RECTS.replace("{img_rects}", inst_img_rects)
   
        user_prompt = USER_PROMPT_IMG2MD.replace("{inst_img_rects}", inst_img_rects)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages_multimodal(system_prompt, user_prompt, pname_image)

        logging.info(f"GFMFIG: convert pdf page {pname_image} to md by gpt started...")
        
        resp = chat_gpt_plain(messages, 
                              model=model,
                              temperature=temperature,
                              top_p=top_p,
                              track_id=f"vllm_gpt_{question_num}")

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="vllm_gpt") 

        if not isinstance(resp, str):
            raise ValueError(f"resp is not str: {resp}")

        content = resp        
        content = strip_llm_format_markers(content)

        logging.info(f"GFMFIG: convert pdf page {pname_image} to md by gpt done")
        return content
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    from ctn2md.utils.util_file import get_root_dir
    from mmbase.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']
    #rects_img = None

    #pname_image = "_work/md_pdf_pages/c3c1d78a-page_3_rects.jpg"
    #rects_img = ['c3c1d78a-img_3_1.jpg']

    pname_image = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
    rects_img = ['5ec48698-img_1_4.jpg',
                 '5ec48698-img_1_3.jpg',
                 '5ec48698-img_1_2.jpg',
                 '5ec48698-img_1_1.jpg']

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    text = generate_full_mds_from_image_gpt(full_path, rects_img=rects_img)
    rich.print(text)
