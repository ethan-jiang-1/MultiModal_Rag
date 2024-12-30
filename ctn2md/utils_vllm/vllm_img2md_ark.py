from typing import List
from dotenv import load_dotenv
import sys
import os
import logging
import rich
from typing import Optional

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from ctn2md.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from ctn2md.utils_llm.llm_base import get_gpt_messages_multimodal, chat_gpt_plain, get_ark_client
from ctn2md.utils_vllm.vllm_img2md_ark_prompt import PROMPT_INSTRUCT_IMG2MD_ARK, PROMPT_INSTRUCT_IMG2MD_ARK_IMG_RECTS

#TODO: ethan_ark_bug:
# DEEPSEEK-V3 P2 - ...
# DEEPSEEK-V3 P28 - heading

def generate_full_mds_from_image_ark(pname_image:str, 
                                     rects_img:List[str] = None, 
                                     model:str = "ep-20241220100411-qb77p", 
                                     question_num:Optional[int] = None) -> str:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if not model.startswith("ep-"): 
            raise ValueError(f"{model} not supporst")

        inst_img_rects = ""

        if rects_img is not None and len(rects_img) > 0:
            rects_img = sorted(rects_img)
            img_rects = ""
            for _, rect_img in enumerate(rects_img):
                img_rects += f"    - {rect_img}\n"
            inst_img_rects = PROMPT_INSTRUCT_IMG2MD_ARK_IMG_RECTS.replace("{img_rects}", img_rects)
   
        user_prompt = PROMPT_INSTRUCT_IMG2MD_ARK.replace("{inst_img_rects}", inst_img_rects)
        #rich.print(user_prompt)

        temperature = 0.01  # 降低温度，使输出更确定性
        top_p = 0.1        # 降低采样范围，减少创造性
        messages = get_gpt_messages_multimodal(None, user_prompt, pname_image)

        logging.info(f"GFMFIG: convert pdf page {pname_image} to md by gpt started...")
        
        client = get_ark_client()
        resp = chat_gpt_plain(messages, 
                              model=model,
                              client=client,
                              temperature=temperature,
                              top_p=top_p,
                              track_id=f"vllm_ark_{question_num}")

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="vllm_gpt") 

        if not isinstance(resp, str):
            raise ValueError(f"resp is not str: {resp}")

        content = resp 
        if '```markdown' in content:
            content = content.replace('```markdown\n', '')
            last_backticks_pos = content.rfind('```')
            if last_backticks_pos != -1:
                content = content[:last_backticks_pos] + content[last_backticks_pos + 3:]        
        #rich.print(content)
        content = content.replace("```", "   ")

        logging.info(f"GFMFIG: convert pdf page {pname_image} to md by gpt done")
        return content
    except Exception as ex: 
        logging.exception(ex)
        rich.print(ex)
        raise ex

if __name__ == "__main__":
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']
    #rects_img = None

    #pname_image = "_work/md_pdf_pages/c3c1d78a-page_3_rects.jpg"
    #rects_img = ['c3c1d78a-img_3_1.jpg']

    # pname_image = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
    # rects_img = ['5ec48698-img_1_4.jpg',
    #              '5ec48698-img_1_3.jpg',
    #              '5ec48698-img_1_2.jpg',
    #              '5ec48698-img_1_1.jpg']
    
    pname_image = "_work/md_pdf_pages/b545fabd-page_2.jpg"
    rects_img = []

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    text = generate_full_mds_from_image_ark(full_path, rects_img=rects_img)
    rich.print(text)
