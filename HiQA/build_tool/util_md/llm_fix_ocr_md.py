import json
#import re
#import time
from openai import AzureOpenAI
from dotenv import load_dotenv
import sys
import os
import logging
#import shutil
#import re

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.util_md.llm_prompt_ocr import USER_PROMPT_MD_SELF_CORRECT, SYSTEM_PROMPT_MD_SELF_CORRECT

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

def fix_ocr_self_correct_markdown(md_text):
    client = AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                         azure_endpoint=os.getenv("OPENAI_BASE_URL"),
                         api_version="2024-02-15-preview")
    try:
        logging.info("start to correct markdown")
        prompt = USER_PROMPT_MD_SELF_CORRECT.replace("{markdown}", md_text)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=_get_gpt_messages(prompt),
            temperature=0.1)
        content = response.choices[0].message.content
        res = json.loads(content.replace("```", "").replace("json", ""))
        text = res['content']
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

    with open(md_old, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text_fixed = fix_ocr_self_correct_markdown(md_text)
    with open(md_new, "w+", encoding='utf-8') as f:
        f.write(md_text_fixed)