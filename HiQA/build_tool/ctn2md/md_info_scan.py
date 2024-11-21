from dotenv import load_dotenv
#import os
import sys
#import logging
#import rich
#import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.utils_bt.util_ctn_type import CtnType

OFM_BY_SKIP = "ofm_skip"
OFM_BY_CONTENT = "ofm_content"
OFM_BY_PAGE = "ofm_page"

def analyze_scan_info(json_result0_pages, doc_type):
    """
    分析 JSON 结果，返回支持判断文档质量的详细数据。

    :param json_result_pages: 按页组织的 JSON 解析结果
    :return: 包含支持判断信息的字典
    """

    result = {
        "total_pages": len(json_result0_pages),  # 文档总页数
        "structured_pages": 0,           # 良好的结构化页面数量
        "scanned_pages": 0,              # 扫描页面数量
        "ocrimg_pages": 0,               # ocr images
        "pages": [],                      # 每页的详细分析结果
        "doc_type": doc_type
    }

    for page in json_result0_pages:
        # 提取页面级信息
        width = page.get("width", 0)
        height = page.get("height", 0)
        items = page.get("items", [])
        images = page.get("images", [])
        
        # 页面总面积
        page_area = width * height

        # 初始化页面统计
        text_blocks = 0
        heading_blocks = 0
        total_text_area = 0
        total_image_area = 0

        # 遍历 items
        for item in items:
            item_type = item.get("type", "").lower()
            bbox = item.get("bBox", None) or item.get("BBox", {})
            item_width = bbox.get("w", 0)
            item_height = bbox.get("h", 0)

            # 累计文本块的面积
            if item_type in {"text", "heading"}:
                text_blocks += 1
                if item_type == "heading":
                    heading_blocks += 1
                if (item_width is not None) and (item_height is not None):
                    total_text_area += item_width * item_height

        # 遍历 images
        total_ocr_images = 0
        for image in images:
            img_width = image.get("width", 0)
            img_height = image.get("height", 0)
            if (img_width is not None) and (img_height is not None):
                total_image_area += img_width * img_height
            ocr = image.get("ocr", None)
            if isinstance(ocr, list) and len(ocr) > 0:
                total_ocr_images += len(ocr)

        # 判断页面是否是结构化页面或扫描页面
        is_structured = (
            text_blocks > 0
            # and heading_blocks > 0
            and total_text_area > 0.5 * page_area
        )
        is_scanned = total_image_area >= 0.8 * page_area

        # 累计全局计数
        if is_structured:
            result["structured_pages"] += 1
        if is_scanned:
            result["scanned_pages"] += 1
        if total_ocr_images > 0:
            result["ocrimg_pages"] += 1

        # 保存当前页的详细数据
        result["pages"].append({
            "page_number": page.get("page", 0),
            "width": width,
            "height": height,
            "text_blocks": text_blocks,
            "heading_blocks": heading_blocks,
            "total_text_area": total_text_area,
            "total_image_area": total_image_area,
            "total_ocr_images": total_ocr_images,
            "page_area": page_area,
            "is_structured": is_structured,
            "is_scanned": is_scanned
        })

    return result


def get_llm_ocr_fix_method(md_info):
    scan_info = md_info.get("scan_info", None)
    if scan_info is None:
        return OFM_BY_SKIP, "no_scan_info"

    ctn_type = md_info.get_ctn_type()
    if ctn_type == CtnType.UNKNOWN or ctn_type == CtnType.XLS:
        return OFM_BY_SKIP, f"ctn_{ctn_type}"

    doc_type = scan_info.get("doc_type", None)
    if doc_type is None:
        raise ValueError("no doc_type in scan_info")

    is_tokens_over_llm_output = md_info.get("is_tokens_over_llm_output", False)
 
    total_pages = scan_info.get("toal_pages", 1)
    scanned_pages = scan_info.get("scanned_pages", 0) 
    structured_pages = scan_info.get("structured_pages", 0)  # 良好的结构化页面数量
    ocrimg_pages = scan_info.get("ocrimg_pages", 0)

    if structured_pages == total_pages:
        return OFM_BY_SKIP, "full_struct"

    if scanned_pages == 0:
        return OFM_BY_SKIP, "no_scan" 

    if ocrimg_pages == 0:
        return OFM_BY_SKIP, "no_ocr"
    
    # TODO: ethan_llm_ocr_fix  need to support llm_ocr_fix multiple pages (>=5) or too many tokens 
    # as llm fix only can support limited output tokens
    if total_pages >= 5:
        if structured_pages / total_pages > 0.8:
            return OFM_BY_SKIP, "stp>0.8"
        if not is_tokens_over_llm_output:
            return OFM_BY_CONTENT, "llm_tklimit<(L)"
        return OFM_BY_PAGE, "??P0??" 
    else:
        if ctn_type == CtnType.PPT:
            return OFM_BY_CONTENT, f"ppt@p{total_pages}"
        if not is_tokens_over_llm_output:
            return OFM_BY_CONTENT, "llm_tklimit<(S)"
        return OFM_BY_PAGE, "??P1??"

