from dotenv import load_dotenv
import os
import sys
#import logging
#import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, PUBLIC_MIFN
class LVLM_IMG_CNT_TYPE:
    GRAPH = "graph"
    IMAGE = "image"
    TABLE = "table"
    LIST = "list"
    TEXT = "text"
    IGNORE = "ignore"
    UNKNOWN = "unknown"

def get_image_cnt_type(md_info:MdInfo, pname_image:str) -> str:
    basename = os.path.basename(pname_image)
    if basename.find("-") == -1:
        return LVLM_IMG_CNT_TYPE.UNKNOWN

    img_name = basename.split("-")[1]
    img_name = img_name.strip()
    if len(img_name) == 0:
        return LVLM_IMG_CNT_TYPE.UNKNOWN

    mctl_lvlm_images_ignore = md_info.get_md_control("mctl_lvlm_images_ignore", None)
    if mctl_lvlm_images_ignore is None:
        return LVLM_IMG_CNT_TYPE.IMAGE
    images_ignore = mctl_lvlm_images_ignore.split(",")
    images_ignore = [item.strip() for item in images_ignore]

    if img_name in images_ignore:
        return LVLM_IMG_CNT_TYPE.IGNORE
    return LVLM_IMG_CNT_TYPE.GRAPH

    
def get_job_id(unique_str:str) -> str:
    from ctn2md.utils.util_file import get_crc32_id
    return get_crc32_id(unique_str)


def is_in_repair_mode(md_info:MdInfo) -> bool:
    mctl_lvlm_repair_pages = md_info.get_md_control("mctl_lvlm_repair_pages",[])  
    if len(mctl_lvlm_repair_pages) > 0:
        return True
    return False

def is_still_in_gen_mode(md_info:MdInfo) -> bool:
    fname_final_sum = md_info.get(PUBLIC_MIFN.FNAME_FINAL_SUM, None)
    if fname_final_sum is None:
        return True 
    return False

