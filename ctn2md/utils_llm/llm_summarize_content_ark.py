from dotenv import load_dotenv
import os
import logging
import rich
from typing import Optional

load_dotenv()

from ctn2md.utils_llm.llm_summarize_content_ark_prompt import SYSTEM_PROMPT_SUMMARIZE, USER_PROMPT_SUMMARIZE
from ctn2md.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from ctn2md.utils_llm.llm_base import get_gpt_messages, chat_gpt_json, get_ark_client


def summarize_doc_keywords_by_ark(doc_title:str, 
                                  full_content:str, 
                                  model:str = "ep-20241220101421-4tj5f", 
                                  question_num:Optional[int] = None) -> dict:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        if not model.startswith("ep-"): 
            raise ValueError(f"f{model} not supporst")

        logging.info(f"start to summarize the content by {model} as question_num: {question_num}")
        prompt = USER_PROMPT_SUMMARIZE.replace("{doc_title}", doc_title).replace("{full_content}", full_content)

        temperature = 0.1
        top_p = 0.9
        messages = get_gpt_messages(SYSTEM_PROMPT_SUMMARIZE, prompt)
        client = get_ark_client()

        resp = chat_gpt_json(messages, 
                             model=model,
                             client=client,
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

    doc_title = "DeepSeek_V3"
    pname_page_content = "_work/ctn2md_papers__DeepSeek_V3_ti/DeepSeek_V3___pdf.md"
    with open(pname_page_content, "r", encoding="utf-8") as f:
        page_content = f.read()

    resp= summarize_doc_keywords_by_ark(doc_title, page_content)
    rich.print(resp)

