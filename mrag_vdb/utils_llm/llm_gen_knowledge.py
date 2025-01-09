from typing import Optional
from dotenv import load_dotenv
import os
import logging
import rich 

load_dotenv()

from mmbase.utils_llm.llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from mmbase.utils_llm.llm_base import get_gpt_messages, chat_gpt_json
from mmbase.utils_llm.llm_base import get_dashscope_client, get_azure_gpt_client, get_ark_client


def gen_knowledge_by_llm(user_input:str, 
                        knowledge:str, 
                        model:str = "", 
                        question_num:Optional[int] = None):
    if question_num is None:
        question_num = get_next_question_num()

    try:
        user_prompt = None 
        system_prompt = None 
        client = None 
        if model.startswith("ep-"): 
            from mrag_vdb.utils_llm.llm_gen_knowledge_ark_prompt import SYSTEM_PROMPT_KNOWLEGE_GEN, USER_PROMPT_KNOWLEGE
            user_prompt = USER_PROMPT_KNOWLEGE
            system_prompt = SYSTEM_PROMPT_KNOWLEGE_GEN
            client = get_ark_client()
        elif model.startswith("gpt"):
            from mrag_vdb.utils_llm.llm_gen_knowledge_gpt_prompt import SYSTEM_PROMPT_KNOWLEGE_GEN, USER_PROMPT_KNOWLEGE
            user_prompt = USER_PROMPT_KNOWLEGE
            system_prompt = SYSTEM_PROMPT_KNOWLEGE_GEN
            client = get_azure_gpt_client()
        elif model.startswith("qwen"):
            from mrag_vdb.utils_llm.llm_gen_knowledge_qwen_prompt import SYSTEM_PROMPT_KNOWLEGE_GEN, USER_PROMPT_KNOWLEGE
            user_prompt = USER_PROMPT_KNOWLEGE
            system_prompt = SYSTEM_PROMPT_KNOWLEGE_GEN
            client = get_dashscope_client()
        else:
            raise ValueError(f"not support model: {model}")

        logging.info(f"start to summarize the content by {model} as question_num: {question_num}")
        prompt = user_prompt.replace("{user_input}", user_input).replace("{knowledge}", knowledge)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(system_prompt, prompt)

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
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    user_input = "你知道什么？"
    knowledge = """ """

    model = "qwen-turbo-1101"
    resp= gen_knowledge_by_llm(user_input, knowledge, model=model)
    rich.print(resp)

