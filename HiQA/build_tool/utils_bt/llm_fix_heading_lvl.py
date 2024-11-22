from dotenv import load_dotenv
import sys
import os
import logging
import rich
import json


if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.utils_bt.llm_fix_heading_lvl_prompt import SYSTEM_PROMPT_FIX_HEADING_LVL, USER_PROMPT_FIX_HEADING_LVL 
from HiQA.utils.util_llm_diag import save_llm_diag_messages, set_question_num
from HiQA.build_tool.utils_bt.llm_base import get_gpt_client, get_gpt_messages, jsons_load_repair


def fix_heading_lvl_markdown(fhl_headings, question_num=400, model="gpt-4o"):
    client = get_gpt_client()
    try:
        if model not in ["gpt-4o-mini", "gpt-4o"]: 
            raise ValueError(f"f{model} not supporst")

        if not isinstance(fhl_headings, dict):
            raise ValueError("fhl_heading need to be dict")

        logging.info(f"start to correct heading level by {model} as questoin_number:{question_num}")

        fhl_headings_json_str = json.dumps(fhl_headings, ensure_ascii=False, indent=4)

        prompt = USER_PROMPT_FIX_HEADING_LVL.replace("{fhl_headings_json_str}", fhl_headings_json_str)      

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(SYSTEM_PROMPT_FIX_HEADING_LVL, prompt)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p)
        resp = jsons_load_repair(response.choices[0].message.content)

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="heading_fix") 

        return resp
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    fhl = {
        "org_doc_title": "座椅STO间隙 P1",
        "org_first_line": "  座椅 STO 间隙",
        "org_heading_lines": [
            "# 目录",
            "# 设计要求",
            "# 靠 背 S T O 间 隙 要 求",
            "# 放倒",
            "# 适途科技"
        ]
    }
   
    new_fhl = fix_heading_lvl_markdown(fhl)
    rich.print(new_fhl)