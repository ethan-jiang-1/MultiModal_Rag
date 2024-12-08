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
from ctn2md.utils_llm.vllm_img2md_gpt import generate_full_mds_from_image_gpt

def _is_in_repair_mode(md_info):
    mctl_lvlm_repair_pages = md_info.get_md_control("mctl_lvlm_repair_pages",[])  
    if len(mctl_lvlm_repair_pages) > 0:
        return True
    return False

def _does_page_need_gen(md_info, page_index):
    if _is_in_repair_mode(md_info):
        mctl_lvlm_repair_pages = md_info.get_md_control("mctl_lvlm_repair_pages",[])
        if page_index in mctl_lvlm_repair_pages:
            return True
        return False   
    return True

def gen_pages_lvlm(md_info):
    pathname_doc = md_info.get_doc_pathname()
    output_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    job_id = get_job_id(pathname_doc)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id

    logging.info(f"GPL: generate image pages job_id:{job_id} is_in_repair_mode: {_is_in_repair_mode(md_info)}")
    image_infos = parse_pdf_to_images(md_info)
    # image_infos
    # image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))

    rich.print(image_infos)
    md_info[MIFN.LVLM_IMAGE_INFOS] = image_infos
    md_info.save()

    pnames_page_md = []
    fnames_imgs = []
    fnames_snps = []
    fnames_page_md_gen = []
    for ndx, image_info in enumerate(image_infos):
        page_index = ndx + 1
        fname_page_name, fname_page_rect_name, fname_rect_images = image_info
        rich.print(page_index, fname_page_name, fname_page_rect_name, fname_rect_images)

        pname_image = os.path.join(output_dir, fname_page_rect_name)
        rects_img = None 
        if len(fname_rect_images) > 0:
            rects_img = fname_rect_images

        fname_page_md = f"page_{page_index}.md"
        pname_page_md = os.path.join(aux_dir, fname_page_md)
        if _does_page_need_gen(md_info, page_index): 
            logging.info(f"GPL: generate page {page_index}...")
            md_page = generate_full_mds_from_image_gpt(pname_image, rects_img)

            mctl_lvlm_notouch_pages = md_info.get_md_control("mctl_lvlm_notouch_pages",[])
            if page_index not in mctl_lvlm_notouch_pages:
                with open(pname_page_md, "w", encoding="utf-8") as f:
                    f.write(md_page)
            fnames_page_md_gen.append(fname_page_md)

        if not _is_in_repair_mode(md_info):
            fnames_imgs.extend(fname_rect_images)
            fnames_snps.append(fname_page_name) 
            pnames_page_md.append(pname_page_md[len(output_dir) + 1:])
    logging.info(f"GPL: page generated: {fnames_page_md_gen} is_in_repair_mode: {_is_in_repair_mode(md_info)}")
    
    if not _is_in_repair_mode(md_info):
        md_info[MIFN.FNAMES_PAGES] = pnames_page_md
        md_info[MIFN.FNAMES_IMGS] = fnames_imgs
        md_info[MIFN.FNAMES_SNPS] = fnames_snps
        md_info.save()

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

