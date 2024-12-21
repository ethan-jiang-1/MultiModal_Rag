from dotenv import load_dotenv
import sys
import os
import logging
import rich 

if "./" not in sys.path:
    sys.path.append("./")
load_dotenv()

from md2vdb.utils_llm.llm_knowledge_gen_gpt_prompt import SYSTEM_PROMPT_KNOWLEGE_GEN, USER_PROMPT_KNOWLEGE
from md2vdb.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from md2vdb.utils_llm.llm_base import get_gpt_messages, chat_gpt_json


def knowlege_gen_by_gpt(user_input, knowledge, model="gpt-4o-mini", question_num=None):
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if model not in ["gpt-4o-mini", "gpt-4o"]: 
            raise ValueError(f"f{model} not supporst")

        logging.info(f"start to summarize the content by {model} as question_num: {question_num}")
        prompt = USER_PROMPT_KNOWLEGE.replace("{user_input}", user_input).replace("{knowledge}", knowledge)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(SYSTEM_PROMPT_KNOWLEGE_GEN, prompt)

        resp = chat_gpt_json(messages, 
                             model=model,
                             temperature=temperature,
                             top_p=top_p,
                             track_id=f"sdk_sum{question_num}")

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="gvi_vllminst") 

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

    user_input = "你知道什么？"
    knowledge = """ """

    resp= knowlege_gen_by_gpt(user_input, knowledge)
    rich.print(resp)

