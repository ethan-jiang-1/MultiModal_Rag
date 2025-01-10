from typing import List
from dotenv import load_dotenv
from llama_parse import LlamaParse


load_dotenv()

MAX_RETRIES = 5

#from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo

def safe_download_images(parser:LlamaParse, json_result:List[dict], md_info:MdInfo) -> List[str]:
    out_dir = md_info.get_out_dir()
    images = parser.get_images(json_result, out_dir)
    return images
