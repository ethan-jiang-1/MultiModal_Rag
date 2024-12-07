import os
import sys
#import re
from typing import List, Tuple, Optional  # , Dict
import logging
import rich

import fitz  # PyMuPDF
import shapely.geometry as sg
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lvlm.lvlm_image_cnt_type import get_image_cnt_type, LVLM_IMG_CNT_TYPE


def _is_near(rect1: BaseGeometry, rect2: BaseGeometry, distance: float = 20) -> bool:
    """
    Check if two rectangles are near each other if the distance between them is less than the target.
    """
    return rect1.buffer(0.1).distance(rect2.buffer(0.1)) < distance


def _is_horizontal_near(rect1: BaseGeometry, rect2: BaseGeometry, distance: float = 100) -> bool:
    """
    Check if two rectangles are near horizontally if one of them is a horizontal line.
    """
    result = False
    if abs(rect1.bounds[3] - rect1.bounds[1]) < 0.1 or abs(rect2.bounds[3] - rect2.bounds[1]) < 0.1:
        if abs(rect1.bounds[0] - rect2.bounds[0]) < 0.1 and abs(rect1.bounds[2] - rect2.bounds[2]) < 0.1:
            result = abs(rect1.bounds[3] - rect2.bounds[3]) < distance
    return result


def _union_rects(rect1: BaseGeometry, rect2: BaseGeometry) -> BaseGeometry:
    """
    Union two rectangles.
    """
    return sg.box(*(rect1.union(rect2).bounds))


def _merge_rects(rect_list: List[BaseGeometry], distance: float = 20, horizontal_distance: Optional[float] = None) -> \
        List[BaseGeometry]:
    """
    Merge rectangles in the list if the distance between them is less than the target.
    """
    merged = True
    while merged:
        merged = False
        new_rect_list = []
        while rect_list:
            rect = rect_list.pop(0)
            for other_rect in rect_list:
                if _is_near(rect, other_rect, distance) or (
                        horizontal_distance and _is_horizontal_near(rect, other_rect, horizontal_distance)):
                    rect = _union_rects(rect, other_rect)
                    rect_list.remove(other_rect)
                    merged = True
            new_rect_list.append(rect)
        rect_list = new_rect_list
    return rect_list


def _adsorb_rects_to_rects(source_rects: List[BaseGeometry], target_rects: List[BaseGeometry], distance: float = 10) -> \
        Tuple[List[BaseGeometry], List[BaseGeometry]]:
    """
    Adsorb a set of rectangles to another set of rectangles.
    """
    new_source_rects = []
    for text_area_rect in source_rects:
        adsorbed = False
        for index, rect in enumerate(target_rects):
            if _is_near(text_area_rect, rect, distance):
                rect = _union_rects(text_area_rect, rect)
                target_rects[index] = rect
                adsorbed = True
                break
        if not adsorbed:
            new_source_rects.append(text_area_rect)
    return new_source_rects, target_rects


def _merge_all_rects(page, rect_list):
    merged_rects = _merge_rects(rect_list, distance=10, horizontal_distance=100)
    merged_rects = [rect for rect in merged_rects if explain_validity(rect) == 'Valid Geometry']

    # 将大文本区域和小文本区域分开处理: 大文本相小合并，小文本靠近合并
    is_large_content = lambda x: (len(x[4]) / max(1, len(x[4].split('\n')))) > 5  # noqa 

    small_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if not is_large_content(x)]
    large_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if is_large_content(x)]
    
    _, merged_rects = _adsorb_rects_to_rects(large_text_area_rects, merged_rects, distance=0.1) # 完全相交
    _, merged_rects = _adsorb_rects_to_rects(small_text_area_rects, merged_rects, distance=5) # 靠近

    # 再次自身合并
    merged_rects = _merge_rects(merged_rects, distance=10)

    # 过滤比较小的矩形
    merged_rects = [rect for rect in merged_rects if rect.bounds[2] - rect.bounds[0] > 20 and rect.bounds[3] - rect.bounds[1] > 20]
    return merged_rects

def _parse_rects(page: fitz.Page, page_index: int) -> List[Tuple[float, float, float, float]]:
    """
    Parse drawings in the page and merge adjacent rectangles.
    """

    # 提取画的内容
    drawings = page.get_drawings()

    # 忽略掉长度小于30的水平直线
    is_short_line = lambda x: abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < 30 # noqa
    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]

    # 转换为shapely的矩形
    rect_list_drawing = [sg.box(*drawing['rect']) for drawing in drawings]
    merged_rects_drawing = _merge_all_rects(page, rect_list_drawing)
    logging.info(f"page_index:{page_index} has number of rect_list_drawing: {len(rect_list_drawing)} after merge: {len(merged_rects_drawing)}")

    # 提取图片区域
    images = page.get_image_info()
    rect_list_image = [sg.box(*image['bbox']) for image in images]
    merged_rects_image = _merge_all_rects(page, rect_list_image)
    logging.info(f"page_index:{page_index} has number of rect_list_image: {len(rect_list_image)} after merge: {len(merged_rects_image)}")

    merged_rects = merged_rects_drawing + merged_rects_image

    return [rect.bounds for rect in merged_rects]

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
        rects = _parse_rects(page, page_index)
        logging.info(f"cal rects for {page_index} done.")

        page_image = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            fname_page_name = f'{job_id}-page_{page_index}.png'
            page_image.save(os.path.join(output_dir, fname_page_name))
        except Exception as ex:
            logging.exception(ex)

        for index, rect in enumerate(rects):
            index += 1

            fitz_rect = fitz.Rect(rect)
            # 保存页面为图片
            pix = page.get_pixmap(clip=fitz_rect, matrix=fitz.Matrix(4, 4))
            draw_red_rect = False
            try:
                fname_rect_name = f'{job_id}-img_{page_index}_{index}.png'
                pname_rect_name = os.path.join(output_dir, fname_rect_name)
                pix.save(pname_rect_name)

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
            fname_page_rect_name = f'{job_id}-page_{page_index}_rects.png'
            page_image_with_rects.save(os.path.join(output_dir, fname_page_rect_name))
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
        if not name.endswith(".png"):
            continue
        if not name.startswith(job_id):
            continue
        pname = os.path.join(output_dir, name)
        if os.path.isfile(pname):
            logging.info(f"clearn image {name}")
            os.unlink(pname)

def get_job_id(unique_str):
    import binascii
    # 将字符串转换为字节
    input_bytes = unique_str.encode('utf-8')

    # 计算CRC32校验和
    crc32_checksum = binascii.crc32(input_bytes)

    # 将CRC32校验和转换为十六进制字符串
    crc32_hex = format(crc32_checksum, '08x')  # '08x'确保输出为8个字符的十六进
    return crc32_hex

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
    
    sel_page_indexes = [8]
    image_infos = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
    rich.print(image_infos)
