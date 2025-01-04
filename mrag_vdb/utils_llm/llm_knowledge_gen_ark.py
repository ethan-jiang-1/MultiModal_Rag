from typing import Dict, Optional
from dotenv import load_dotenv
import os
import logging
import rich 

load_dotenv()

from mrag_vdb.utils_llm.llm_knowledge_gen_ark_prompt import SYSTEM_PROMPT_KNOWLEGE_GEN, USER_PROMPT_KNOWLEGE
from mrag_vdb.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from mrag_vdb.utils_llm.llm_base import get_gpt_messages, chat_gpt_json, get_ark_client


def knowlege_gen_by_ark(user_input:str, 
                        knowledge:str, 
                        model:str = "ep-20241220101421-4tj5f", 
                        question_num:Optional[int] = None) -> Dict:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if not model.startswith("ep-"): 
            raise ValueError(f"f{model} not supporst")

        logging.info(f"start to summarize the content by {model} as question_num: {question_num}")
        prompt = USER_PROMPT_KNOWLEGE.replace("{user_input}", user_input).replace("{knowledge}", knowledge)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(SYSTEM_PROMPT_KNOWLEGE_GEN, prompt)
        client = get_ark_client()

        resp = chat_gpt_json(messages, 
                             model=model,
                             client=client,
                             temperature=temperature,
                             top_p=top_p,
                             track_id=f"sdk_sum{question_num}")

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="kgbq") 

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

    resp= knowlege_gen_by_ark(user_input, knowledge)
    rich.print(resp)

