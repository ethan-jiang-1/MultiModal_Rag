from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.gen_lvlm.lvlm_pdf_to_images import get_job_id, parse_pdf_to_images
from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN

def gen_pages_lvlm(md_info):
    pathname_doc = md_info.get_doc_pathname()
    #output_dir = md_info.get_out_dir()
    job_id = get_job_id(pathname_doc)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id

    logging.info(f"gen_pages_lvlm: generate image pages job_id:{job_id}")
    image_infos = parse_pdf_to_images(md_info)
    # image_infos
    # image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))

    rich.print(image_infos)
    md_info[MIFN.LVLM_IMAGE_INFOS] = image_infos
    md_info.save()

    for ndx, image_info in enumerate(image_infos):
        page_index = ndx + 1
        fname_page_name, fname_page_rect_name, fname_rect_images = image_info
        rich.print(page_index, fname_page_name, fname_page_rect_name, fname_rect_images)
        pass

    return md_info.save()

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    output_dir = MdInfo.get_suggested_out_dir(doc_pathname)

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    
    ret = gen_pages_lvlm(md_info)
    rich.print(ret)

