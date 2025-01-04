import os
from typing import List, Tuple, Optional
import logging
import rich

import fitz  # PyMuPDF
import pymupdf

from dotenv import load_dotenv
load_dotenv()

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lvlm.lvlm_base import get_image_cnt_type, LVLM_IMG_CNT_TYPE
from ctn2md.gen_lvlm.gs0_pdf_page_to_region import gs0_parse_non_text_rects_in_page
from ctn2md.gen_lvlm.gs1_pdf_page_to_region import gs1_parse_non_text_rects_in_page
from ctn2md.gen_lvlm.gs2_pdf_page_to_region import gs2_parse_non_text_rects_in_page
from ctn2md.utils_gen.gen_base import get_job_id
from ctn2md.utils_gen.gen_base import is_still_in_gen_mode
from ctn2md.gen_lvlm._draw_redrect_on_page import draw_redrect_on_page

IMG_EXT = "jpg"  # or "png"
#IMG_EXT = "png"  # or "png"
JPG_QUALITY = 90 # 95


def _get_non_text_rects(md_info:MdInfo, 
                        page:pymupdf.Page, 
                        page_index:int, 
                        pname_page_name:str, 
                        mctl_lvlm_region_detect:Optional[str] = None) -> List[Tuple[float, float, float, float]]:
    if mctl_lvlm_region_detect is None:
        mctl_lvlm_region_detect = md_info.get_md_control("mctl_lvlm_region_detect", "gs0")
    logging.info(f"cal rects for {page_index} starts...")
    if mctl_lvlm_region_detect == "gs0":
        rects_non_text = gs0_parse_non_text_rects_in_page(md_info, page, page_index, pname_page_name)
    elif mctl_lvlm_region_detect == "gs1":
        rects_non_text = gs1_parse_non_text_rects_in_page(md_info, page, page_index, pname_page_name)
    elif mctl_lvlm_region_detect == "gs2": 
        rects_non_text = gs2_parse_non_text_rects_in_page(md_info, page, page_index, pname_page_name)
    else:
        raise ValueError(f"unspoorted mctl_lvlm_region_detect {mctl_lvlm_region_detect}")
    logging.info(f"cal rects for {page_index} done.")
    return rects_non_text


def _assign_final_doc_cnt_type(md_info:MdInfo, pdf_document:fitz.Document):
    from ctn2md.utils.util_ctn_type import CTN_TYPE
    doc_type = md_info.get_doc_type()
    md_info[MIFN.DOC_CTN_TYPE] = CTN_TYPE.get_ctn_type_by_doc_type(doc_type)
    if pdf_document is not None and len(pdf_document) > 0:
        page1 = pdf_document[0]
        page_width, page_height = page1.mediabox_size
        if md_info[MIFN.DOC_CTN_TYPE] == CTN_TYPE.PDF:
            if page_width > page_height:
                md_info[MIFN.DOC_CTN_TYPE] = CTN_TYPE.PPT
        md_info.save()

def parse_pdf_to_images(md_info: MdInfo, 
                        sel_page_indexes: Optional[List[int]] = None, 
                        mctl_lvlm_region_detect: Optional[str] = None) -> List[Tuple[str, str, List[str]]]:
    """
    Parse PDF to images and save to output_dir.
    """

    output_dir = md_info.get_out_dir()
    pdf_path = md_info.get_doc_pathname()
    job_id = md_info[MIFN.LVLM_CUR_JOB_ID]

    if not os.path.isdir(output_dir):
        raise ValueError(f"output dir does not exit {output_dir}")
    if len(job_id) == 0:
        raise ValueError(f"invalid job_id {job_id}")

    if not is_still_in_gen_mode(md_info):
        clean_previous_images(output_dir, job_id)

    if mctl_lvlm_region_detect is None:
        mctl_lvlm_region_detect = md_info.get_md_control("mctl_lvlm_region_detect", "gs0")

    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    image_infos = []

    for page_index, page in enumerate(pdf_document):
        page_index += 1

        fname_page_name = f'{job_id}-page_{page_index}.{IMG_EXT}'
        pname_page_name = os.path.join(output_dir, fname_page_name)
        fname_page_rect_name = f'{job_id}-page_{page_index}_rects.{IMG_EXT}'  
        pname_page_rect_name = os.path.join(output_dir, fname_page_rect_name)

        if not is_still_in_gen_mode(md_info):
            if sel_page_indexes is not None:
                if page_index not in sel_page_indexes:
                    logging.info(f"skip {page_index} due to sel_page_indexes")
                    continue     

        logging.info(f'parse page: {page_index}')
        fname_rect_images = []

        page_image = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            page_image.save(pname_page_name, jpg_quality=JPG_QUALITY)
            logging.info(f"pname_page_name saved {pname_page_name}")
        except Exception as ex:
            logging.exception(ex)
  
        logging.info(f"cal rects for page:{page_index} starts {mctl_lvlm_region_detect}...")
        rects_non_text = _get_non_text_rects(md_info, page, page_index, pname_page_name, mctl_lvlm_region_detect=mctl_lvlm_region_detect)
        logging.info(f"cal rects for page:{page_index} done.")

        for index, rect_non_text in enumerate(rects_non_text):
            index += 1

            fitz_rect = fitz.Rect(rect_non_text)
            # 保存页面为图片
            pix = page.get_pixmap(clip=fitz_rect, matrix=fitz.Matrix(4, 4))
            draw_red_rect = False
            try:
                fname_rect_name = f'{job_id}-img_{page_index}_{index}.{IMG_EXT}'
                pname_rect_name = os.path.join(output_dir, fname_rect_name)
                pix.save(pname_rect_name, jpg_quality=JPG_QUALITY)

                ict = get_image_cnt_type(md_info, pname_rect_name)
                if ict in [LVLM_IMG_CNT_TYPE.GRAPH, LVLM_IMG_CNT_TYPE.IMAGE, LVLM_IMG_CNT_TYPE.TABLE]:
                    fname_rect_images.append(fname_rect_name)
                    draw_red_rect = True
            except Exception as ex:
                logging.exception(ex)

            if draw_red_rect:
                draw_redrect_on_page(page, fitz_rect, fname_rect_name)

        page_image_with_rects = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            page_image_with_rects.save(pname_page_rect_name, jpg_quality=JPG_QUALITY)
            logging.info(f"pname_page_rect_name saved {pname_page_rect_name}")
        except Exception as ex:
            logging.exception(ex)

        image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))

    _assign_final_doc_cnt_type(md_info, pdf_document)
    pdf_document.close()
    return image_infos

def clean_previous_images(output_dir:str, job_id:str):
    if not os.path.isdir(output_dir):
        return
    names = os.listdir(output_dir)
    for name in names:
        if not name.endswith(f".{IMG_EXT}"):
            continue
        if not name.startswith(job_id):
            continue
        pname = os.path.join(output_dir, name)
        if os.path.isfile(pname):
            logging.info(f"clearn image {name}")
            os.unlink(pname)

if __name__ == "__main__":
    #setup_logger_handlers(logging.DEBUG)
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    #sel_page_indexes = [8]

    #doc_pathname = "datasrc/exam/raw_docs/Survey of different Large Language Model Architectures.pdf"
    #sel_page_indexes = [3,4]
    #mctl_lvlm_region_detect = "gs0"

    #doc_pathname = "datasrc/exam/raw_docs/Survey of different Large Language Model Architectures.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/papers/ “AI+应用”百花齐放，新质生产力前景广阔pdf.pdf"
    #sel_page_indexes = [1]
    #mctl_lvlm_region_detect = "gs0"

    doc_pathname = "datasrc/exam/raw_docs/papers/DeepSeek_V3.pdf"
    sel_page_indexes = [2, 28]
    mctl_lvlm_region_detect = "gs2"

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    

    image_infos = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes, mctl_lvlm_region_detect=mctl_lvlm_region_detect)
    rich.print(image_infos)
