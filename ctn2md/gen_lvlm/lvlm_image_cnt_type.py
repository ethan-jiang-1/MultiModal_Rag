#import os
import sys

#import logging
#import rich

if './' not in sys.path:
    sys.path.append("./")

#from ctn2md.utils.util_logging import setup_logger_handlers
#from ctn2md.src.md_info_base import MdInfo, MIFN
class LVLM_IMG_CNT_TYPE:
    GRAPH = "graph"
    IMAGE = "image"
    TABLE = "table"
    LIST = "list"
    TEXT = "text"
    UNKNOWN = "unknown"

def get_image_cnt_type(md_info, pname_image):
    if pname_image.find("-") == -1:
        return LVLM_IMG_CNT_TYPE.UNKNOWN

    img_name = pname_image.split("-")[1]
    mctl_lvlm_image_to_content_type = md_info.get_md_control("mctl_lvlm_image_to_content_type", None)
    if mctl_lvlm_image_to_content_type is None:
        return LVLM_IMG_CNT_TYPE.IMAGE
    val = mctl_lvlm_image_to_content_type.get(img_name, None)
    if val is not None:
        return val
    return LVLM_IMG_CNT_TYPE.GRAPH


