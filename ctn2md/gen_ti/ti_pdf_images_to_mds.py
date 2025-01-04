import os
import sys
from typing import List, Optional
import logging


if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MIFN, MdInfo
from ctn2md.src.md_page_spe import SpecialPage
from ctn2md.gen_ti._ti_gen_md import convert_image_to_md
from ctn2md.gen_ti._ti_update_img_ref import update_page_md_with_ref_imgs

g_question_num = 9000

def _does_page_need_gen(pname_page_md:str, md_info:MdInfo) -> bool:
    if not os.path.isfile(pname_page_md):
        return True

    if SpecialPage.does_page_have_failed_mark(pname_page_md):
        return True

    return False

def _gen_page_md_by_ti(pname_image:str, pname_page_md:str):
    logging.info(f"GPMBL: generate page {os.path.basename(pname_page_md)}...")

    md_page = convert_image_to_md(pname_image)

    with open(pname_page_md, "w", encoding="utf-8") as f:
        f.write(md_page)

def convert_images_to_mds(md_info:MdInfo, fnames_page_image: List[str], sel_page_ndxs:Optional[List[int]] = None) -> int:
    output_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()

    if fnames_page_image is None or len(fnames_page_image) == 0:
        fnames_page_image = md_info.get(MIFN.FNAMES_SNPS, [])

    pnames_page_md = []
    fnames_imgs = []
    fnames_snps = []
    fnames_page_md_gen = []

    logging.info(f"GITM: generate pages from images")
    cnt_page_gen = 0
    map_page2ref_imgs = {}
    for ndx, fname_page_name in enumerate(fnames_page_image):
        page_index = ndx + 1

        if sel_page_ndxs is not None:
            if page_index not in sel_page_ndxs:
                continue

        pname_image = os.path.join(output_dir, fname_page_name)
        logging.info(f"GITM: generate page {page_index} from {pname_image}")

        fnames_ref_name = []
        fname_page_md = f"page_{page_index}.md"
        pname_page_md = os.path.join(aux_dir, fname_page_md)
        if _does_page_need_gen(pname_page_md, md_info): 
            if not SpecialPage.does_page_have_touched_mark(pname_page_md):
                _gen_page_md_by_ti(pname_image, pname_page_md)
                cnt_page_gen += 1
                fnames_ref_name = update_page_md_with_ref_imgs(md_info, page_index, pname_page_md)  
                map_page2ref_imgs[page_index] = [fnames_ref_name]
            fnames_page_md_gen.append(fname_page_md)
        else:
            logging.info(f"skip gen {pname_page_md}")
            fnames_page_md_gen.append(fname_page_md)

        if sel_page_ndxs is None:
            fnames_imgs.extend(fnames_ref_name) 
            fnames_snps.append(fname_page_name) 
            pnames_page_md.append(pname_page_md[len(output_dir) + 1:])

    if MIFN.TI_MAP_PAGE2REF_IMGS not in md_info:
        md_info[MIFN.TI_MAP_PAGE2REF_IMGS] = {}
    for key, value in map_page2ref_imgs.items():
        md_info[MIFN.TI_MAP_PAGE2REF_IMGS][key] = value

    logging.info(f"GITM: pages have been generated: {fnames_page_md_gen} from images")
    
    if sel_page_ndxs is None:
        md_info[MIFN.FNAMES_MD_PAGES] = pnames_page_md
        md_info[MIFN.FNAMES_IMGS] = fnames_imgs
        md_info[MIFN.FNAMES_SNPS] = fnames_snps
        md_info.save()
    return cnt_page_gen

if __name__ == "__main__":
    setup_logger_handlers()

    #pname_md_info = "_output/ctn2md_papers__深度学习在视电阻率快速反演中的研究_ti/_info.json"
    #sel_page_ndxs = [12]
    pname_md_info = "_output/ctn2md_papers____AI+应用_百花齐放_新质生产力前景广阔pdf_ti/_info.json"
    sel_page_ndxs = [1]

    md_info = MdInfo(pname_md_info)  
    ret = convert_images_to_mds(md_info, None, sel_page_ndxs=sel_page_ndxs)  
    print("page generated:", ret)


