import logging
from typing import List, Tuple
import fitz
import rich
import os
import cv2
import numpy as np

from dotenv import load_dotenv
load_dotenv()


from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.gen_lvlm._gs2_pdf_page_to_region import (
    extract_picture_regions,
    call_doclayout_yolo_endpoint
)
from ctn2md.src.md_info_base import MIFN
from ctn2md.utils_gen.gen_base import get_job_id


def gs2_parse_picture_regions_in_page(
    page_index: int, 
    pname_page_name: str,
    page: fitz.Page,
    conf_threshold: float = 0.5
) -> List[Tuple[float, float, float, float]]:
    """使用YOLO检测页面中的图片区域，并转换为PDF points单位
    """
    try:
        # 获取PDF页面尺寸（points）
        pdf_width, pdf_height = page.rect.width, page.rect.height
        
        # 获取图像尺寸（pixels）
        img_array = np.fromfile(pname_page_name, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Cannot read image: {pname_page_name}")
        height, width = img.shape[:2]
        
        response = call_doclayout_yolo_endpoint(pname_page_name)
        if response:
            yolo_regions = extract_picture_regions(response, conf_threshold=conf_threshold)
            
            # 转换坐标系统（只需要将像素转换为points）
            pdf_regions = []
            for x1, y1, x2, y2 in yolo_regions:
                # 简单的像素到points的转换
                minx = (x1 / width) * pdf_width
                miny = (y1 / height) * pdf_height
                maxx = (x2 / width) * pdf_width
                maxy = (y2 / height) * pdf_height
                
                pdf_regions.append((minx, miny, maxx, maxy))
            
            return pdf_regions
        
        logging.warning(f"Page {page_index}: YOLO detection failed")
        return []
        
    except Exception as e:
        logging.error(f"Page {page_index}: Error processing {pname_page_name}: {str(e)}")
        return []

def gs2_parse_non_text_rects_in_page(
    md_info: MdInfo, 
    page: fitz.Page, 
    page_index: int, 
    pname_page_name: str
) -> List[Tuple[float, float, float, float]]:
    """兼容旧接口的包装函数"""
    return gs2_parse_picture_regions_in_page(page_index, pname_page_name, page)

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    doc_pathname = "datasrc/exam/raw_docs/papers/LongRAG.pdf"
    page_no = 8

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    
    pdf_document = fitz.open(doc_pathname)
    page = pdf_document[page_no - 1] # 0-based index

    pname_page_name = f"_work/{os.path.basename(doc_pathname)}_{page_no}.jpg"
    page.get_pixmap(matrix=fitz.Matrix(1, 1)).save(pname_page_name)

    merged_rects_bounds= gs2_parse_non_text_rects_in_page(md_info, page, page_no, pname_page_name)
    rich.print(merged_rects_bounds)