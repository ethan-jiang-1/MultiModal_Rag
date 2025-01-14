import os
from typing import List, Tuple, Optional # , Dict
import logging
import rich

from dotenv import load_dotenv
load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MIFN, MdInfo
from ctn2md.md_info.md_page_spe import SpecialPage
from ctn2md.gen_lvlm.image2mds.lvlm_image_to_md import gen_page_md_by_lvlm
def _does_page_need_gen(pname_page_md:str, md_info:MdInfo) -> bool:
    if not os.path.isfile(pname_page_md):
        return True

    if SpecialPage.does_page_have_failed_mark(pname_page_md):
        return True

    return False

def convert_images_to_mds(md_info:MdInfo, image_infos: List[Tuple[str, List[str]]], sel_page_ndxs:Optional[List[int]] = None) -> int:
    output_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()

    if image_infos is None or len(image_infos) == 0:
        image_infos = md_info.get(MIFN.LVLM_IMAGE_INFOS, [])

    pnames_page_md = []
    fnames_imgs = []
    fnames_snps = []
    fnames_page_md_gen = []
    mctl_lvlm_img2md_model = md_info.get_md_control("mctl_lvlm_img2md_model", "gpt")

    logging.info(f"GITM: generate pages from images")
    cnt_page_gen = 0
    for ndx, image_info in enumerate(image_infos):
        page_index = ndx + 1

        if sel_page_ndxs is not None:
            if page_index not in sel_page_ndxs:
                continue

        fname_page_name, fname_page_rect_name, fname_rect_images = image_info
        rich.print(page_index, fname_page_name, fname_page_rect_name, fname_rect_images)

        pname_image = os.path.join(output_dir, fname_page_rect_name)
        rects_img = None 
        if len(fname_rect_images) > 0:
            rects_img = fname_rect_images

        fname_page_md = f"page_{page_index}.md"
        pname_page_md = os.path.join(aux_dir, fname_page_md)
        if _does_page_need_gen(pname_page_md, md_info): 
            if not SpecialPage.does_page_have_touched_mark(pname_page_md):
                gen_page_md_by_lvlm(md_info, mctl_lvlm_img2md_model, pname_image, rects_img, pname_page_md)
                cnt_page_gen += 1
            fnames_page_md_gen.append(fname_page_md)
        else:
            logging.info(f"skip gen {pname_page_md}")
            fnames_page_md_gen.append(fname_page_md)

        if sel_page_ndxs is None:
            fnames_imgs.extend(fname_rect_images)
            fnames_snps.append(fname_page_name) 
            pnames_page_md.append(pname_page_md[len(output_dir) + 1:])

    logging.info(f"GITM: pages have been generated: {fnames_page_md_gen} from images")
    
    if sel_page_ndxs is None:
        md_info[MIFN.FNAMES_MD_PAGES] = pnames_page_md
        md_info[MIFN.FNAMES_IMGS] = fnames_imgs
        md_info[MIFN.FNAMES_SNPS] = fnames_snps
        md_info.save()
    return cnt_page_gen

if __name__ == "__main__":
    setup_logger_handlers()

    pname_md_info = "_output/ctn2md_papers__DeepSeek_V3_lvlm/_info.json"
    sel_page_ndxs = [3]

    md_info = MdInfo(pname_md_info)  
    ret = convert_images_to_mds(md_info, None, sel_page_ndxs=sel_page_ndxs)  
    print("page generated:", ret)


