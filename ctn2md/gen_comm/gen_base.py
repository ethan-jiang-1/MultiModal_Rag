from dotenv import load_dotenv
import sys

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, PUBLIC_MIFN

    
def get_job_id(unique_str:str) -> str:
    from ctn2md.utils.util_file import get_crc32_id
    return get_crc32_id(unique_str)

def is_still_in_gen_mode(md_info:MdInfo) -> bool:
    fname_final_sum = md_info.get(PUBLIC_MIFN.FNAME_FINAL_SUM, None)
    if fname_final_sum is None:
        return True 
    return False
