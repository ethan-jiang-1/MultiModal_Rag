from dotenv import load_dotenv

load_dotenv()

from ctn2md.utils_vllm.vllm_img_description_qwen_prompt import TEXT_PROMPT_INST_VLLM_GEN_QAS
from ctn2md.utils_vllm.vllm_img_description_qwen_prompt import TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE

(TEXT_PROMPT_INST_VLLM_GEN_QAS, TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE)

TEXT_IMG_DESCRIPTION = "请简单用**一个段落**，描述一下这张图片。"