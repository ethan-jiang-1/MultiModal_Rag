import os
import sys
from typing import List, Tuple # , Optional  # , Dict
import logging
import rich

import fitz  # PyMuPDF
#import shapely.geometry as sg
#from shapely.geometry.base import BaseGeometry
#from shapely.validation import explain_validity

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lvlm.lvlm_image_cnt_type import get_image_cnt_type, LVLM_IMG_CNT_TYPE
from ctn2md.gen_lvlm.lvlm_pdf_page_to_image import parse_non_text_rects_in_page
from ctn2md.gen_lvlm.lvlm_base import get_job_id


IMG_EXT = "jpg"  # or "png"
JPG_QUALITY = 90 # 95


def _draw_red_rect_on_page(page, fitz_rect, fname_rect_name):
    # # 在页面上绘制红色矩形
    big_fitz_rect = fitz.Rect(fitz_rect.x0 - 1, fitz_rect.y0 - 1, fitz_rect.x1 + 1, fitz_rect.y1 + 1)
    # 空心矩形
    page.draw_rect(big_fitz_rect, color=(1, 0, 0), width=1)
    # 画矩形区域(实心)
    # page.draw_rect(big_fitz_rect, color=(1, 0, 0), fill=(1, 0, 0))
    # 在矩形内的左上角写上矩形的索引name，添加一些偏移量
    text_x = fitz_rect.x0 + 2
    text_y = fitz_rect.y0 + 10
    text_rect = fitz.Rect(text_x, text_y - 9, text_x + 80, text_y + 2)
    # 绘制白色背景矩形
    page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1))
    # 插入带有白色背景的文字
    page.insert_text((text_x, text_y), fname_rect_name, fontsize=10, color=(1, 0, 0))


def parse_pdf_to_images(md_info: MdInfo, sel_page_indexes=None) -> List[Tuple[str, str, List[str]]]:
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

    clean_previous_images(output_dir, job_id)

    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    image_infos = []

    for page_index, page in enumerate(pdf_document):
        page_index += 1
        if sel_page_indexes is not None:
            if page_index not in sel_page_indexes:
                continue
        logging.info(f'parse page: {page_index}')
        fname_rect_images = []
        logging.info(f"cal rects for {page_index} starts...")
        rects_non_text, _ = parse_non_text_rects_in_page(md_info, page, page_index)
        logging.info(f"cal rects for {page_index} done.")

        page_image = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            fname_page_name = f'{job_id}-page_{page_index}.{IMG_EXT}'
            pname_page_name = os.path.join(output_dir, fname_page_name)
            page_image.save(pname_page_name, jpg_quality=JPG_QUALITY)
        except Exception as ex:
            logging.exception(ex)

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
                _draw_red_rect_on_page(page, fitz_rect, fname_rect_name)

        page_image_with_rects = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            fname_page_rect_name = f'{job_id}-page_{page_index}_rects.{IMG_EXT}'
            pname_page_rect_name = os.path.join(output_dir, fname_page_rect_name)
            page_image_with_rects.save(pname_page_rect_name, jpg_quality=JPG_QUALITY)
        except Exception as ex:
            logging.exception(ex)

        image_infos.append((fname_page_name, fname_page_rect_name, fname_rect_images))

    pdf_document.close()
    return image_infos

def clean_previous_images(output_dir, job_id):
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

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    
    sel_page_indexes = [8]
    image_infos = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
    rich.print(image_infos)
