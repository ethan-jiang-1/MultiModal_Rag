from typing import List
from dotenv import load_dotenv
import os
import logging
import rich

load_dotenv()

from ctn2md.gen_base.utils.gen_utils import is_still_in_gen_mode
from ctn2md.gen_lvlm.lvlm_pdf_pages_to_images import parse_pdf_to_images
from ctn2md.gen_lvlm.image2mds.lvlm_images_to_mds import convert_images_to_mds
from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MdInfo, MIFN


def gen_pages_lvlm(md_info:MdInfo, mdcontrols:dict = None, skip_gen_mds: bool = False, sel_page_indexes: List[int] = None) -> str:
    job_id = md_info.get_unique_job_id()

    if isinstance(mdcontrols, dict):
        md_info.update_mdcontrols(mdcontrols)

    logging.info(f"GPL: generate image pages job_id:{job_id}")
    # image_infos
    # image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))
    # Step1: convert all pdf pages to images (image_infos: with region images)
    image_infos = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
    rich.print(image_infos)
    md_info[MIFN.LVLM_IMAGE_INFOS] = image_infos
    md_info.save()

    # Step2: Convert images (image_infos: with region images) to mds by LVLM
    if not skip_gen_mds or is_still_in_gen_mode(md_info):
        logging.info(f"GPL: convert images to mds")
        convert_images_to_mds(md_info, image_infos)
        logging.info(f"GPL: page generated")
    else:
        logging.warning(f"GPL: skip convert images to mds")

    return md_info.save()

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    doc_pathname = "datasrc/exam/raw_docs/papers/DeepSeek_V3.pdf"

    #sel_page_indexes = []
    sel_page_indexes = None

    #mdcontrols = None
    mdcontrols = {"mctl_lvlm_region_detect": "gs0"}  
    skip_gen_mds = True

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')
    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    
    ret = gen_pages_lvlm(md_info, mdcontrols=mdcontrols, skip_gen_mds=skip_gen_mds)
    rich.print(ret)

