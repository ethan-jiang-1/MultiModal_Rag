import sys
from typing import Tuple 

import rich
import json_repair

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MdInfo


from ctn2md.utils_llm.llm_gen_vllm_instruction_gpt import gen_vllm_instruction_by_gpt
from ctn2md.utils_llm.llm_gen_vllm_instruction_qwen import gen_vllm_instruction_by_qwen
from ctn2md.utils_llm.llm_gen_vllm_instruction_ark import gen_vllm_instruction_by_ark
from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils_vllm.vllm_img_description_gpt import generate_image_description_by_gpt
from ctn2md.utils_vllm.vllm_img_description_ark import generate_image_description_by_ark

g_question_num = 9000


def _get_page_instruction(md_info:MdInfo, doc_title:str, content_around:str) -> str:
    global g_question_num
    mctl_ti_img_relevance_model = md_info.get_md_control("mctl_ti_img_relevance_model", "ark")
    if mctl_ti_img_relevance_model == "qwen":
        instruction = gen_vllm_instruction_by_qwen(doc_title, content_around, question_num=g_question_num)
    elif mctl_ti_img_relevance_model == "gpt":
        instruction = gen_vllm_instruction_by_gpt(doc_title, content_around, question_num=g_question_num)
    elif mctl_ti_img_relevance_model == "ark":
        instruction = gen_vllm_instruction_by_ark(doc_title, content_around, question_num=g_question_num)
    else:
        raise ValueError(f"unsupport model {mctl_ti_img_relevance_model}")
    g_question_num += 1
    return instruction

def _gen_figure_info(md_info:MdInfo, doc_title:str, content_around:str, image_path_or_url:str) -> dict:
    instruction = _get_page_instruction(md_info, doc_title, content_around)
    mctl_ti_img_caption_model = md_info.get_md_control("mctl_ti_img_caption_model", "ark")
    if mctl_ti_img_caption_model == "qwen":
        resp = generate_image_description_by_qwen(image_path_or_url, instruction=instruction)
    elif mctl_ti_img_caption_model == "gpt":
        resp = generate_image_description_by_gpt(image_path_or_url, instruction=instruction)        
    elif mctl_ti_img_caption_model == "ark":
        resp = generate_image_description_by_ark(image_path_or_url, instruction=instruction)     
    else:
        raise ValueError(f"unsupport model: {mctl_ti_img_caption_model}")   
    if resp is None:
        raise ValueError("resp is None")
    resp_json = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
    #rich.print(resp_json)
    return resp_json

def get_img_alt_text_and_description(md_info:MdInfo, img_url:str, content:str) -> Tuple[str, str]:
    doc_title = md_info.get_doc_title()
    resp = _gen_figure_info(md_info, doc_title, content, img_url)
    rich.print(resp)
    return resp["FigureName"], resp["PictureDescription"]