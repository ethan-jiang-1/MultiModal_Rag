from dotenv import load_dotenv
import sys
import os
import logging
import rich
import json


if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from ctn2md.utils_llm.llm_fix_heading_lvl_prompt import SYSTEM_PROMPT_FIX_HEADING_LVL, USER_PROMPT_FIX_HEADING_LVL 
from ctn2md.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from ctn2md.utils_llm.llm_base import get_gpt_client, get_gpt_messages, jsons_load_repair

def fix_heading_lvl_markdown(fhl_org, model="gpt-4o",  question_num=None):
    client = get_gpt_client()
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if model not in ["gpt-4o-mini", "gpt-4o"]: 
            raise ValueError(f"f{model} not supporst")

        if not isinstance(fhl_org, dict):
            raise ValueError("fhl_heading need to be dict")

        logging.info(f"start to correct heading level by {model} as questoin_number:{question_num}")

        fhl_org_json_str = json.dumps(fhl_org, ensure_ascii=False, indent=4)

        prompt = USER_PROMPT_FIX_HEADING_LVL.replace("{fhl_org_json_str}", fhl_org_json_str)      

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
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="fhl_heading") 

        return resp
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    fhl_org = {
        "org_doc_title": "业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）",
        "org_first_line": "# 技术服务合同",
        "org_heading_lines": [
            [
                "# 技术服务合同",
                0
            ],
            [
                "# 比亚迪汽车工业有限公司",
                7
            ],
            [
                "# 上海适途汽车技术有限公司",
                194
            ],
            [
                "# 技术服务合同V5.0",
                705
            ],
            [
                "# 1 工作划分",
                149
            ],
            [
                "# 2 合同工作的执行",
                1135
            ],
            [
                "# 技术服务合同V5.0",
                705
            ]
        ]
    }
    new_fhl = fix_heading_lvl_markdown(fhl_org)
    rich.print(new_fhl)