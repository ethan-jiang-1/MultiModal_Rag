from dotenv import load_dotenv
import sys
import os
import logging
import rich 

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.utils_bt.llm_fix_vl_instruction_prompt import SYSTEM_PROMPT_GEN_VLLM_CONTEXT, USER_PROMPT_GEN_VLLM_CONTEXT
from HiQA.build_tool.utils_bt.llm_fix_vl_instruction_prompt import TEXT_PROMPT_INST_VLLM_IMG
from HiQA.utils.util_llm_diag import save_llm_diag_messages, set_question_num
from HiQA.build_tool.utils_bt.llm_base import get_gpt_client, get_gpt_messages, jsons_load_repair

def get_vllm_instruction(doc_title, page_content, question_num=200, model="gpt-4o-mini"):
    client = get_gpt_client()
    try:
        logging.info(f"start to make vllm instruction by {model} as question_num: {question_num}")
        prompt = USER_PROMPT_GEN_VLLM_CONTEXT.replace("{doc_title}", doc_title).replace("{page_content}", page_content)

        #model = "gpt-4o"
        #model = "gpt-4o-mini"
        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(SYSTEM_PROMPT_GEN_VLLM_CONTEXT, prompt)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            timeout=120)
        content = response.choices[0].message.content
        resp = jsons_load_repair(content)

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="ocr_fix") 

        page_context = resp['page_context']

        instruction = TEXT_PROMPT_INST_VLLM_IMG.replace("{page_context}", page_context)
        return instruction
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    doc_title = "5. back panel 与环境匹配工程校核_P2"
    page_content = """  back panel 与环境匹配工程校核

1
 Restricted © SOTOS 2017. All Rights Reserved."""


    instruction= get_vllm_instruction(doc_title, page_content)
    rich.print(instruction)

