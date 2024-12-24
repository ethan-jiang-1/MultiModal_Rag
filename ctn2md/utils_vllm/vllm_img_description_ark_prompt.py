import sys
if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils_vllm.vllm_img_description_qwen_prompt import TEXT_PROMPT_INST_VLLM_GEN_QAS
from ctn2md.utils_vllm.vllm_img_description_qwen_prompt import TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE

(TEXT_PROMPT_INST_VLLM_GEN_QAS, TEXT_PROMPT_INST_VLLM_IMG_RELEVANCE)