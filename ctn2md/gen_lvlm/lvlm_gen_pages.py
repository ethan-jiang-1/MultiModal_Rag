from dotenv import load_dotenv
#import os
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
from ctn2md.src.md_info_base import MIFN

def gen_pages_lvlm(md_info):
    pathname_doc = md_info.get_doc_pathname()
    output_dir = md_info.get_out_dir()
    job_id = get_job_id(pathname_doc)

    logging.info(f"gen_pages_lvlm: generate image pages job_id:{job_id}")
    image_infos = parse_pdf_to_images(pathname_doc, output_dir=output_dir, job_id=job_id)
    # image_infos
    # image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))

    rich.print(image_infos)
    md_info[MIFN.LVLM_IMAGE_INFOS] = image_infos
    md_info.save()

if __name__ == "__main__":
    setup_logger_handlers()
