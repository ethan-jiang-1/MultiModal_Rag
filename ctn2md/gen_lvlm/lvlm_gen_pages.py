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

from ctn2md.gen_lvlm.lvlm_base import get_job_id, is_in_repair_mode
from ctn2md.gen_lvlm.lvlm_pdf_pages_to_images import parse_pdf_to_images
from ctn2md.gen_lvlm.lvlm_pdf_images_to_mds import convert_images_to_mds
from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN


def gen_pages_lvlm(md_info):
    pathname_doc = md_info.get_doc_pathname()
    job_id = get_job_id(pathname_doc)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id

    logging.info(f"GPL: generate image pages job_id:{job_id} is_in_repair_mode: {is_in_repair_mode(md_info)}")
    # image_infos
    # image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))
    # Step1: convert all pdf pages to images (image_infos: with region images)
    image_infos = parse_pdf_to_images(md_info)
    rich.print(image_infos)
    md_info[MIFN.LVLM_IMAGE_INFOS] = image_infos
    md_info.save()

    # Convert images (image_infos: with region images) to mds by LVLM
    convert_images_to_mds(md_info, image_infos)

    return md_info.save()

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    
    ret = gen_pages_lvlm(md_info)
    rich.print(ret)

