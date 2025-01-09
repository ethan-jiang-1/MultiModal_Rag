from typing import Dict, Optional
from dotenv import load_dotenv
import os
import logging
import rich 

load_dotenv()

from mrag_vdb.utils.util_llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from mrag_vdb.utils_llm.llm_base import get_gpt_messages, chat_gpt_json
from mrag_vdb.utils_llm.llm_base import get_ark_client, get_azure_gpt_client, get_dashscope_client

def check_img_relevance_by_llm(user_query:str, 
                               llm_answer: str, 
                               knowledge_context: str, 
                               numbered_image_descriptions: str, 
                               model:str = "", 
                               question_num:Optional[int] = None) -> Dict:
    if question_num is None:
        question_num = get_next_question_num()

    try:
        user_prompt = None 
        system_prompt = None
        client = None
        if model.startswith("ep-"): 
            from mrag_vdb.utils_llm.llm_image_relevance_ark_prompt import SYSTEM_PROMPT_IMAGE_RELEVANCE, USER_PROMPT_IMAGE_RELEVANCE
            user_prompt = USER_PROMPT_IMAGE_RELEVANCE
            system_prompt = SYSTEM_PROMPT_IMAGE_RELEVANCE
            client = get_ark_client()
        elif model.startswith("gpt"):
            from mrag_vdb.utils_llm.llm_image_relevance_gpt_prompt import SYSTEM_PROMPT_IMAGE_RELEVANCE, USER_PROMPT_IMAGE_RELEVANCE
            user_prompt = USER_PROMPT_IMAGE_RELEVANCE
            system_prompt = SYSTEM_PROMPT_IMAGE_RELEVANCE
            client = get_azure_gpt_client()
        elif model.startswith("qwen"):
            from mrag_vdb.utils_llm.llm_image_relevance_qwen_prompt import SYSTEM_PROMPT_IMAGE_RELEVANCE, USER_PROMPT_IMAGE_RELEVANCE
            user_prompt = USER_PROMPT_IMAGE_RELEVANCE
            system_prompt = SYSTEM_PROMPT_IMAGE_RELEVANCE
            client = get_dashscope_client()
        else:
            raise ValueError(f"not support model: {model}")

        logging.info(f"start to summarize the content by {model} as question_num: {question_num}")
        prompt = user_prompt.replace("{user_query}", user_query).replace("{llm_answer}", llm_answer)
        prompt = prompt.replace("{knowledge_context}", knowledge_context).replace("{numbered_image_descriptions}", numbered_image_descriptions)

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
        save_llm_diag_messages(messages, resp, model=model, temperature=temperature, top_p=top_p, prefix="cirbl") 

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

    user_query = "法规要求的前后排座椅距离是多少"
    llm_answer = "前后排座椅的距离应大于600毫米，后排座椅的设计目标值为大于612毫米。"
    context = "## 设计要求\n\n2\n**设计 要求**\n\n设 计 的 座 椅 位 置 的 数 量 - 中 国 法 规\n\n截 图 后 测 量 以 下 参 数 ， 看 是 否 满 足 要 求\n\n|序号|描述|法规要求|设计目标值|\n|---|---|---|---|\n|S 9 . 2|前 后 排 座 椅 距 离|＞ 6 0 0 . 0 m m|后 排 座 ＞ 6 1 2 m m|\n| |( 第 一 排 和 第 二 排 或 第 二 排 和 第 三 排 )| |椅|\n**适途科技**"
    numberd_image_description = """
                                 0) 图像展示了一个广阔的山地景观，前景中有两个人正在攀登山坡。山坡上覆盖着灰色的碎石和少量的雪。远处可以看到一条蜿蜒的小路穿过山谷，山谷两侧是绿色和黄色的草地。背景是连绵起伏的山脉，天空中有一些云朵。
                                 1) 图像展示了一辆车辆的前后排座椅的垂直剖面图。前排座椅和后排座椅的位置通过点A、B、C和D标记。图中标注了两个S9.2e尺寸，表示前后排座椅之间的距离。此外，还标注了从车辆地板到座椅顶部的高度为620毫米。
                                 """

    model = "gpt-4o-mini"
    resp= check_img_relevance_by_llm(user_query, llm_answer, context, numberd_image_description, model=model)
    rich.print(resp)

