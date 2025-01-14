from dotenv import load_dotenv

load_dotenv()

#from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MdInfo, PUBLIC_MIFN


def is_still_in_gen_mode(md_info:MdInfo) -> bool:
    fname_final_sum = md_info.get(PUBLIC_MIFN.FNAME_FINAL_SUM, None)
    if fname_final_sum is None:
        return True 
    return False
