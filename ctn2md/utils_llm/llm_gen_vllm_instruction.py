from dotenv import load_dotenv
import os
import logging
import rich 
from typing import Optional

load_dotenv()

from ctn2md.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from ctn2md.utils_llm.llm_base import get_gpt_messages, chat_gpt_json
from ctn2md.utils_llm.llm_base import get_ark_client, get_azure_gpt_client, get_dashscope_client
from ctn2md.utils_vllm.vllm_img_description_qwen_prompt import TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE

def gen_vllm_instruction_llm(doc_title:str, 
                             page_content:str, 
                             model:str = "qwen-turbo-1101", 
                             question_num:Optional[int] = None) -> str:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        user_prompt = None 
        system_prompt = None
        client = None
        if model.startswith("ep-"): 
            from ctn2md.utils_llm.llm_gen_vllm_instruction_qwen_prompt import SYSTEM_PROMPT_GEN_VLLM_CONTEXT, USER_PROMPT_GEN_VLLM_CONTEXT
            user_prompt = USER_PROMPT_GEN_VLLM_CONTEXT
            system_prompt = SYSTEM_PROMPT_GEN_VLLM_CONTEXT
            client = get_ark_client()
        elif model.startswith("gpt"):
            from ctn2md.utils_llm.llm_gen_vllm_instruction_gpt_prompt import SYSTEM_PROMPT_GEN_VLLM_CONTEXT, USER_PROMPT_GEN_VLLM_CONTEXT
            user_prompt = USER_PROMPT_GEN_VLLM_CONTEXT
            system_prompt = SYSTEM_PROMPT_GEN_VLLM_CONTEXT
            client = get_azure_gpt_client()
        elif model.startswith("qwen"):
            from ctn2md.utils_llm.llm_gen_vllm_instruction_qwen_prompt import SYSTEM_PROMPT_GEN_VLLM_CONTEXT, USER_PROMPT_GEN_VLLM_CONTEXT
            user_prompt = USER_PROMPT_GEN_VLLM_CONTEXT 
            system_prompt = SYSTEM_PROMPT_GEN_VLLM_CONTEXT
            client = get_dashscope_client()
        else:
            raise ValueError(f"not support model: {model}")

        logging.info(f"start to make vllm instruction by {model} as question_num: {question_num}")
        prompt = user_prompt.replace("{doc_title}", doc_title).replace("{page_content}", page_content)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(system_prompt, prompt)

        resp = chat_gpt_json(messages, 
                             model=model,
                             client=client,
                             temperature=temperature,
                             top_p=top_p,
                             track_id=f"gvi_vllinst_{question_num}")

        set_question_num(question_num)
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="gvi_vllminst") 

        page_context = resp['page_context']
        page_content_language = resp['page_content_language']

        instruction = TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE.replace("{page_context}", page_context).replace("{page_content_language}",page_content_language)
        return instruction
    except Exception as ex: 
        logging.exception(ex)
        raise ex

if __name__ == "__main__":
    from ctn2md.utils.util_file import get_root_dir
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    dir_root = get_root_dir()
    os.chdir(dir_root)

    doc_title = "5. back panel 与环境匹配工程校核_P2"
    page_content = """  back panel 与环境匹配工程校核

1
 Restricted © SOTOS 2017. All Rights Reserved."""
    
    model = "qwen-plus"
    instruction= gen_vllm_instruction_llm(doc_title, page_content, model=model)
    rich.print(instruction)

