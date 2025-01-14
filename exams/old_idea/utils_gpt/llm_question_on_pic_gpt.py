import os
import logging
import sys
import rich
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils.util_file import get_root_dir
from mmbase.utils.util_logging import setup_logger_handlers
from exams.old_idea.utils_gpt.llm_question_on_pic_gpt_prompt import SYSTEM_PROMPT_GPT4_QAGEN, USER_PROMPT_GPT4_QAGEN
from mmbase.utils_llm_debug.llm_diag import save_llm_diag_messages, set_question_num, get_next_question_num
from mmbase.utils_llm.llm_base import get_gpt_messages, chat_gpt_json

# Constants
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.95

def gen_questions_on_pic_by_gpt(
    container_name: str, 
    img_desc: str, 
    model: str = DEFAULT_MODEL, 
    question_num: Optional[int] = None
) -> dict:
    """
    使用GPT模型基于图片描述生成问题。

    Args:
        container_name: 容器名称
        img_desc: 图片描述文本
        model: 使用的GPT模型名称，默认为'gpt-4o'
        question_num: 问题编号，如果为None则自动生成

    Returns:
        dict: 生成的问题数据
    """
    try:
        if question_num is None:
            question_num = get_next_question_num()

        if not model.startswith(("gpt-4o-mini", "gpt-4o")): 
            raise ValueError(f"Model {model} not supported")
    
        logging.info(f"Generating questions using {model}...")
        prompt = USER_PROMPT_GPT4_QAGEN.replace("{container_name}", container_name).replace("{img_desc}", img_desc)

        messages = get_gpt_messages(SYSTEM_PROMPT_GPT4_QAGEN, prompt)
        resp = chat_gpt_json(
            messages, 
            model=model,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            track_id=f"gqo_picdesc_{question_num}"
        )

        set_question_num(question_num)
        save_llm_diag_messages(
            messages, 
            resp, 
            model=model, 
            temperature=DEFAULT_TEMPERATURE, 
            top_p=DEFAULT_TOP_P, 
            prefix="gqo_picdesc"
        ) 
        return resp
    except Exception as ex: 
        logging.exception(f"Error generating questions: {ex}")
        raise

if __name__ == '__main__':
    try:
        # 初始化设置
        setup_logger_handlers()
        dir_root = get_root_dir()

        # 测试图片配置
        image_url = "_work/md_pdf_pages/5ec48698-page_1_rects.jpg"
        full_path = os.path.join(dir_root, image_url)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image file not found: {full_path}")

        # 获取容器名称
        container_name = os.path.basename(os.path.dirname(image_url))
        instruction = f"这是一张在'{container_name}'文件中的图片， 请详细描述一下这张图片。 要被用到知识库建设中，所以知识性细节越多越好."   

        # 生成图片描述
        logging.info("Generating image description...")
        img_desc = generate_image_description_by_qwen(full_path, instruction=instruction)
        print("Image Description:")
        print(img_desc)
        print()

        # 生成问题
        logging.info("Generating questions...")
        questions = gen_questions_on_pic_by_gpt(container_name, img_desc)
        rich.print("Generated Questions:")
        rich.print(questions)
        print()

    except Exception as e:
        logging.exception(f"Error in main execution: {e}")
        logging.error(f"Error in main execution: {e}")
        sys.exit(1)