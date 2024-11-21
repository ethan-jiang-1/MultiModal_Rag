from openai import AzureOpenAI
from dotenv import load_dotenv
import sys
import os
import logging
import json_repair

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.util_md.llm_fix_ocr_md_prompt import SYSTEM_PROMPT_MD_SELF_CORRECT 
from HiQA.build_tool.util_md.llm_fix_ocr_md_prompt import USER_PROMPT_MD_SELF_CORRECT_PDF 
from HiQA.build_tool.util_md.llm_fix_ocr_md_prompt import USER_PROMPT_MD_SELF_CORRECT_PPT 
from HiQA.build_tool.util_md.llm_fix_ocr_md_prompt import USER_PROMPT_MD_SELF_CORRECT_DOC 
#from HiQA.build_tool.util_md.llm_fix_ocr_md_prompt import USER_PROMPT_MD_SELF_CORRECT_XLS 
from HiQA.build_tool.util_md.util_ctn_type import CtnType
from HiQA.utils.util_llm_diag import save_llm_diag_messages, set_question_num

def _get_gpt_messages(prompt):
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT_MD_SELF_CORRECT
        },
        {
            "role": "user",
            "content": prompt
        },
    ]
    return messages

def fix_ocr_self_correct_markdown(md_text, doc_type, question_num=100, model="gpt4-o"):
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    try:
        logging.info(f"start to correct markdown from doc_type:{doc_type} by {model} as questoin_number:{question_num}")
        ctn_type = CtnType.get_ctn_type(doc_type)

        if ctn_type == CtnType.PDF:
            prompt = USER_PROMPT_MD_SELF_CORRECT_PDF.replace("{markdown}", md_text)
        elif ctn_type == CtnType.PPT:
            prompt = USER_PROMPT_MD_SELF_CORRECT_PPT.replace("{markdown}", md_text)
        elif ctn_type == CtnType.DOC:
            prompt = USER_PROMPT_MD_SELF_CORRECT_DOC.replace("{markdown}", md_text)
        else:
            raise ValueError(f"unknown ctn_type {ctn_type}")            

        temperature = 0.1
        top_p = 0.9
        messages=_get_gpt_messages(prompt)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            timeout=120)
        content = response.choices[0].message.content
        resp = json_repair.repair_json(content, ensure_ascii=True, return_objects=True)

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="ocr_fix") 

        text = resp['content']
        return text
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    md_old = "_work/tmp/AIGC时代的人力资源管理进化(徐刚).md"
    md_new = "_work/tmp/AIGC时代的人力资源管理进化(徐刚)_ocr_fixed.md"
    doc_type = "pptx"

    with open(md_old, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text_fixed = fix_ocr_self_correct_markdown(md_text, doc_type)
    with open(md_new, "w+", encoding='utf-8') as f:
        f.write(md_text_fixed)