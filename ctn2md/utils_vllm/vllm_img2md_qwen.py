import os
import logging
import sys
from typing import List
import rich
from dotenv import load_dotenv


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

from ctn2md.utils_vllm.vllm_img2md_qwen_prompt import PROMPT_INSTRUCT_IMG2MD_QWEN_START, PROMPT_INSTRUCT_IMG2MD_QWEN_START_IMG_RECTS, PROMPT_INSTRUCT_IMG2MD_QWEN_CONTINUE
from ctn2md.utils_llm.llm_base import get_dashscope_client, get_gpt_messages_multimodal, chat_gpt_plain

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
        inst_img_rects = PROMPT_INSTRUCT_IMG2MD_QWEN_START_IMG_RECTS.replace("{img_rects}", img_rects)

    (PROMPT_INSTRUCT_IMG2MD_QWEN_CONTINUE)
    
    prompt_start = PROMPT_INSTRUCT_IMG2MD_QWEN_START.replace("{inst_img_rects}", inst_img_rects)

    messages = get_gpt_messages_multimodal(None, prompt_start, pname_image)

    client = get_dashscope_client()

    logging.info(f"GFMFI: generate_full_mds_from_image started... {pname_image}")
    resp_str = chat_gpt_plain(messages, model=model, client=client, temperature=0.01, top_p=0.95)    
    
    # 过滤掉开头和结尾的 markdown 标记
    resp_str = resp_str.strip()  # 先去除首尾空白
    if resp_str.startswith("```markdown\n"):
        resp_str = resp_str[len("```markdown\n"):]
    elif resp_str.startswith("```\n"):
        resp_str = resp_str[len("```\n"):]
        
    if resp_str.endswith("\n```"):
        resp_str = resp_str[:-4]
    
    #rich.print(resp_str)
    return resp_str

    
    # # The model name 'qwen-vl-max-0809' is the identity of 'Qwen2-VL-72B'.
    # logging.info(f"GFMFI: generate_full_mds_from_image started... {pname_image}")
    # full_content = ""
    # for loop in range(4):
    #     logging.info(f"GFMFI: start loop:{loop}")
    #     response = chat_qwen_mm(messages, model=model, retries=retries, backoff_in_seconds=backoff_in_seconds, track_id="gfmdiq")
    #     if not isinstance(response, str):
    #         logging.error("GFMFI: response is not str")
    #         continue
        
    #     text_content = response.replace("```markdown", "").replace("```", "")
    #     full_content += text_content
    #     if text_content.find("[ocr_end]") != -1:
    #         logging.info(f"GFMFI: finished [ocr_end] loop@{loop}")
    #         break
    #     if response.output.finish_reason:
    #         logging.info(f"GFMFI: finished finish_reason @{loop}")
    #         break
    #     if len(messages) == 1:
    #         messages.append(
    #             {'role': response.output.choices[0].message.role,
    #              'content': [{'text': text_content}]})
    #         messages.append(
    #             {'role': 'user',
    #              'content':[{'text': PROMPT_INSTRUCT_IMG2MD_QWEN_CONTINUE}]})
    #     else:
    #         messages[1]["content"] = [{'text': full_content}]


    # full_content = full_content.replace("[ocr_end]", "")
    # #rich.print(messages)
    # logging.info(f"GFMFI: total output length {len(full_content)}")
    # logging.info(f"GFMFI: generate_full_mds_from_image ended. {pname_image}")
    # return full_content


if __name__ == '__main__':
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    dir_root = get_root_dir()
    setup_logger_handlers()

    #pname_image = "_work/md_samples/e479b909-page_1_rects.png"
    #rects_img = ['e479b909-img_1_1.png']

    pname_image = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
    rects_img = ['5ec48698-img_1_4.jpg',
                 '5ec48698-img_1_3.jpg',
                 '5ec48698-img_1_2.jpg',
                 '5ec48698-img_1_1.jpg']

    full_path = os.path.join(dir_root, pname_image)
    container_name = os.path.basename(os.path.dirname(pname_image))

    text = generate_full_mds_from_image_qwen(full_path, rects_img=rects_img)
    rich.print(text)
