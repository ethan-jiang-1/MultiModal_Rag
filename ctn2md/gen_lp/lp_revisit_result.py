from dotenv import load_dotenv
#import os
import sys
#import logging
import rich
#import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src.md_info_base import MdInfo, MIFN, OFM
from ctn2md.utils.util_tokenizer import get_token_encoding

#TODO: ethan_output_token check if we are able to make GPTo output more then 3*1024 token. and how
#MAX_OUTPUT_TOKEN = 8*1024
MAX_OUTPUT_TOKEN = 8*1024

def _analyse_page_from_lp_page(page, lp_scan_info):
    lp_scan_info_pages = lp_scan_info["pages"]

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
        elif item_type == "table":
            print(item_type) # item_type = "table"
        else:
            print(item_type)

    # 遍历 images
    total_ocr_images = 0
    for image in images:
        img_width = image.get("width", 0)
        img_height = image.get("height", 0)
        if (img_width is not None) and (img_height is not None):
            total_image_area += img_width * img_height
        ocr = image.get("ocr", None)
        if isinstance(ocr, list) and len(ocr) > 0:
            total_ocr_images += len(ocr) # [ {'x': 661, 'y': 14, 'w': 59, 'h': 50, 'confidence': '0.2615117255774045', 'text': '3)'},..] text out of image 

    # 判断页面是否是结构化页面或扫描页面
    is_structured = (
        text_blocks > 0
        # and heading_blocks > 0
        and total_text_area > 0.5 * page_area
    )
    is_scanned = total_image_area >= 0.8 * page_area

    # 累计全局计数
    if is_structured:
        lp_scan_info["structured_pages"] += 1
    if is_scanned:
        lp_scan_info["scanned_pages"] += 1
    if total_ocr_images > 0:
        lp_scan_info["ocrimg_pages"] += 1

    # 保存当前页的详细数据
    lp_scan_info_pages.append({
        "page_number": page.get("page", 0),
        "width": round(width, 2),
        "height": round(height,2),
        "text_blocks": text_blocks,
        "heading_blocks": heading_blocks,
        "total_text_area": round(total_text_area, 2),
        "total_image_area": round(total_image_area, 2),
        "total_ocr_images": total_ocr_images,  # text out of ocr img does not contribute to md_text ?!
        "page_area": round(page_area, 2),
        "is_structured": is_structured,
        "is_scanned": is_scanned,
    })


def _analyze_lp_scan_info(md_info, json_result0_pages, doc_type):
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
        _analyse_page_from_lp_page(page, result)

    return result

def _calculate_tokens_large_text(text, chunk_size=2048, stop_check_over_max=False):
    """
    针对超长文本的 Token 数量计算，分块处理。
    
    :param text: 输入的长字符串
    :param chunk_size: 每块的最大字符数
    :param encoding_name: 编码器名称
    :return: Token 数量
    """
    # 获取编码器
    encoding = get_token_encoding()
    
    # 初始化 Token 计数器
    total_tokens = 0
    
    # 分块处理
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        tokens = encoding.encode(chunk)
        total_tokens += len(tokens)

        if total_tokens > MAX_OUTPUT_TOKEN:
            return total_tokens
    
    return total_tokens

def _cal_recommended_ofm_mode(md_info, md_text):
    ofm = md_info.get_md_control("mctl_ofm", None)
    ofm_reason = ""
    if ofm is None or ofm == OFM.BY_AUTO:
        total_tokens = _calculate_tokens_large_text(md_text, stop_check_over_max=True)
        mp_is_num_tokens_over_llm_output_limit = (total_tokens > MAX_OUTPUT_TOKEN)
        md_info.set_md_params("mp_is_num_tokens_over_llm_output_limit", mp_is_num_tokens_over_llm_output_limit)

        ofm, ofm_reason = _get_llm_ocr_fix_method_from_scan_info(md_info)
        md_info.set_md_params("mp_ofm", ofm)
        md_info.set_md_params("mp_ofm_reason", ofm_reason)


def _get_llm_ocr_fix_method_from_scan_info(md_info):
    scan_info = md_info.get(MIFN.LP_SCAN_INFO, None)
    if scan_info is None:
        return OFM.BY_SKIP, "scan_info=None"

    ctn_type = md_info.get_ctn_type()
    if ctn_type == CTN_TYPE.UNKNOWN or ctn_type == CTN_TYPE.XLS:
        return OFM.BY_SKIP, f"ctn_type={ctn_type}"

    doc_type = scan_info.get("doc_type", None)
    if doc_type is None:
        raise ValueError("no doc_type in scan_info")

    mp_is_num_tokens_over_llm_output_limit = md_info.get_md_params("mp_is_num_tokens_over_llm_output_limit", False)
 
    total_pages = scan_info.get("total_pages", 1)
    scanned_pages = scan_info.get("scanned_pages", 0) 
    structured_pages = scan_info.get("structured_pages", 0)  # 良好的结构化页面数量
    ocrimg_pages = scan_info.get("ocrimg_pages", 0)

    if structured_pages == total_pages:
        return OFM.BY_SKIP, "structured_pages=tp"

    if scanned_pages == 0:
        return OFM.BY_SKIP, "scanned_pages=0" 

    if ocrimg_pages == 0:
        return OFM.BY_SKIP, "ocrimg_pages=0"
    
    # TODO: ethan_llm_ocr_recommendation  need to support llm_ocr_fix multiple pages (>=5) or too many tokens 
    # as we push ocr into gen proc, so the best result here seeems we just recommend which page need premium ocr
    # as llm fix only can support limited output tokens
    if total_pages >= 5:
        if structured_pages / total_pages >= 0.8:
            return OFM.BY_SKIP, "stp>=0.8"
        if not mp_is_num_tokens_over_llm_output_limit:
            return OFM.BY_CONTENT, "llm_tklimit<(L)"
        return OFM.BY_PAGE, "??P0??" 
    else:
        if ctn_type == CTN_TYPE.PPT:
            return OFM.BY_CONTENT, f"ppt@tp={total_pages}"
        if not mp_is_num_tokens_over_llm_output_limit:
            return OFM.BY_CONTENT, "llm_tklimit<(S)"
        return OFM.BY_PAGE, "??P1??"


def post_scan_llamaparse_result(md_info, json_result=None):
    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "r") as f: 
        md_text = f.read()

    if json_result is not None and len(json_result) > 0:
        json_result0_pages = json_result[0].get("pages", None)
        if json_result0_pages is not None:
            doc_pathname = md_info.get_doc_pathname()
            doc_type = doc_pathname.split(".")[-1].lower()
            _analyze_lp_scan_info(md_info, json_result0_pages, doc_type)

    _cal_recommended_ofm_mode(md_info, md_text)

    #TODO, ethan_ocr_at_gen if a page found have strong ocr trace, we should rebuild the content by stitching 
    pass


if __name__ == "__main__":
    
    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    md_info = MdInfo(md_info_path)

    ret = post_scan_llamaparse_result(md_info)
    rich.print(ret)