from dotenv import load_dotenv
import os
import sys

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo

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


