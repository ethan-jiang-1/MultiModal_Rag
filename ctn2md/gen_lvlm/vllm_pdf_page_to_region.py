import os
import sys
import logging
import rich
import fitz  

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lvlm.lvlm_base import get_job_id
from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.utils_vllm.vllm_img2region_gpt import generate_regions_from_image_gpt
from ctn2md.utils_vllm.vllm_img2region_qwen import generate_regions_from_image_qwen


"""
返回是 bounds list, 每一个 bounds 如下：
(x_min, y_min, x_max, y_max)
#### **参数说明**
1. **`x_min`**: 
- 矩形左边界的 x 坐标。
- 表示该矩形区域在页面上的最左端位置。
2. **`y_min`**:
- 矩形下边界的 y 坐标。
- 表示该矩形区域在页面上的最下端位置。
3. **`x_max`**:
- 矩形右边界的 x 坐标。
- 表示该矩形区域在页面上的最右端位置。
4. **`y_max`**:
- 矩形上边界的 y 坐标。
- 表示该矩形区域在页面上的最上端位置。

#### **坐标系统**
- **绝对坐标**：
- 坐标基于 PDF 页面尺寸的绝对单位，通常是以点（point）为单位（1 点 = 1/72 英寸）。
- `(0, 0)` 通常是 PDF 页面左下角的起始点。
- `x` 值从左到右增加，`y` 值从下到上增加。
"""

def vllm_parse_non_text_rects_in_page_by_gpt(md_info, page, page_index, pname_page_name):
    """
    Parse non-text rectangular regions in a PDF page using GPT and return their bounds.

    Parameters:
    - md_info: Metadata information (not used in this function, reserved for future extensions).
    - page: The page object containing media box size and other page properties.
    - page_index: The index of the page (useful for debugging/logging).
    - pname_page_name: The file path of the image extracted from the PDF page.

    Returns:
    - A list of bounds representing rectangular regions as (x_min, y_min, x_max, y_max).
    """
    try:
        # Get page dimensions
        page_width, page_height = page.mediabox_size

        # Step 1: Call GPT function to generate regions
        resp = generate_regions_from_image_gpt(pname_page_name)
        
        # Step 2: Process the GPT response to generate rects
        rects = []
        for region in resp:
            # Check if the region has the required fields
            if "type" in region and "bbox" in region and isinstance(region["bbox"], list) and len(region["bbox"]) == 4:
                region_type = region["type"]
                x_min_rel, y_min_rel, x_max_rel, y_max_rel = region["bbox"]

                # Convert relative coordinates to absolute coordinates
                x_min = x_min_rel * page_width
                y_min = y_min_rel * page_height
                x_max = x_max_rel * page_width
                y_max = y_max_rel * page_height

                # Handle specific types: image, chart, table
                if region_type in ["image", "chart", "table"]:
                    rects.append((x_min, y_min, x_max, y_max))
                else:
                    logging.warning(f"Page {page_index}: Ignored unsupported region type '{region_type}' with bbox {region['bbox']}")
            else:
                logging.warning(f"Page {page_index}: Invalid region format: {region}")

        # Return the processed rectangles
        return rects

    except Exception as e:
        # Log the error and return an empty list in case of failure
        logging.exception(f"Error parsing non-text rectangles for page {page_index}: {e}")
        return []

def vllm_parse_non_text_rects_in_page_by_qwen(md_info, page, page_index, pname_page_name):
    """
    Parse non-text rectangular regions in a PDF page using GPT and return their bounds.

    Parameters:
    - md_info: Metadata information (not used in this function, reserved for future extensions).
    - page: The page object containing media box size and other page properties.
    - page_index: The index of the page (useful for debugging/logging).
    - pname_page_name: The file path of the image extracted from the PDF page.

    Returns:
    - A list of bounds representing rectangular regions as (x_min, y_min, x_max, y_max).
    """
    try:
        # Get page dimensions
        page_width, page_height = page.mediabox_size

        # Step 1: Call GPT function to generate regions
        resp = generate_regions_from_image_qwen(pname_page_name)
        
        # Step 2: Process the GPT response to generate rects
        rects = []
        for region in resp:
            # Check if the region has the required fields
            if "type" in region and "bbox" in region and isinstance(region["bbox"], list) and len(region["bbox"]) == 4:
                region_type = region["type"]
                x_min_rel, y_min_rel, x_max_rel, y_max_rel = region["bbox"]

                # Convert relative coordinates to absolute coordinates
                x_min = x_min_rel * page_width
                y_min = y_min_rel * page_height
                x_max = x_max_rel * page_width
                y_max = y_max_rel * page_height

                # Handle specific types: image, chart, table
                if region_type in ["image", "chart", "table"]:
                    rects.append((x_min, y_min, x_max, y_max))
                else:
                    logging.warning(f"Page {page_index}: Ignored unsupported region type '{region_type}' with bbox {region['bbox']}")
            else:
                logging.warning(f"Page {page_index}: Invalid region format: {region}")

        # Return the processed rectangles
        return rects

    except Exception as e:
        # Log the error and return an empty list in case of failure
        logging.exception(f"Error parsing non-text rectangles for page {page_index}: {e}")
        return []

if __name__ == "__main__":
    
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/attention_is_all_you_need.pdf"
    doc_pathname = "datasrc/exam/raw_docs/LongRAG.pdf"
    page_no = 8

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='lvlm')

    job_id = get_job_id(doc_pathname)

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.LVLM_CUR_JOB_ID] = job_id
    
    pdf_document = fitz.open(doc_pathname)
    page = pdf_document[page_no - 1] # 0-based index
    pname_page_name = os.path.join(output_dir, f"test_page-{page_no-1}.jpg")
    page_image = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    page_image.save(pname_page_name, jpg_quality=90)

    rects_bounds = vllm_parse_non_text_rects_in_page_by_gpt(md_info, page, page_no, pname_page_name)
    rich.print(rects_bounds)

    rects_bounds = vllm_parse_non_text_rects_in_page_by_qwen(md_info, page, page_no, pname_page_name)
    rich.print(rects_bounds)

