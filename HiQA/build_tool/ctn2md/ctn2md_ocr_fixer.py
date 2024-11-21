from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.util_md.llm_fix_ocr_md import fix_ocr_self_correct_markdown
from HiQA.build_tool.ctn2md.md_info_base import save_md_info, load_md_info, get_doc_type
from HiQA.build_tool.ctn2md.md_info_scan import get_llm_ocr_fix_method, OFM_BY_CONTENT, OFM_BY_PAGE, OFM_BY_SKIP
from HiQA.utils.tokenizer import get_token_encoding

#TODO: check if we are able to make GPTo output more then 3*1024 token. and how
MAX_OUTPUT_TOKEN = 3*1024

#import tiktoken

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

def _fix_ocr_by_stiche_pages(md_text, md_info, out_dir):
    fnames_pages = md_info.get("fnames_pages", {})
    if not fnames_pages:
        raise ValueError("fnames_pages is empty")
    
    md_text_fixed = ""
    for fname_page in fnames_pages:
        pathname = os.path.join(out_dir, fname_page)
        with open(pathname, 'r', encoding='utf8') as f:
            md_page = f.read()
        doc_type = get_doc_type(md_info)
        md_page_fixed = fix_ocr_self_correct_markdown(md_page, doc_type) 
        md_text_fixed += md_page_fixed + "\n"

    return md_text_fixed      

def _fix_ocr_by_proc_whole(md_text, md_info, out_dir):
    total_tokens = _calculate_tokens_large_text(md_text, stop_check_over_max=True)
    if total_tokens > MAX_OUTPUT_TOKEN: 
        md_text_fixed = _fix_ocr_by_stiche_pages(md_text, md_info, out_dir)
    else:
        doc_type = get_doc_type(md_info)
        md_text_fixed = fix_ocr_self_correct_markdown(md_text, doc_type)  
    return md_text_fixed  

def fix_ocr_content_by_gpt(md_info_path, ofm=None):
    out_dir = os.path.dirname(md_info_path)
    md_info = load_md_info(md_info_path)
    if md_info is None:
        return None, None 

    fname_output_s0_md = md_info.get("fname_output_s0_md", None)
    if fname_output_s0_md is None:
        return None, None 

    pname_s0 = os.path.join(out_dir, fname_output_s0_md)
    with open(pname_s0, "r", encoding="utf8") as f:
        md_text = f.read()

    if ofm is None:
        ofm = get_llm_ocr_fix_method(md_info)

    sel_ofm = ofm
    if ofm == OFM_BY_PAGE:
        total_tokens = _calculate_tokens_large_text(md_text, stop_check_over_max=True)
        if total_tokens < MAX_OUTPUT_TOKEN:
            sel_ofm = OFM_BY_CONTENT

    logging.info(f"OFM: ofm:{ofm} sel_ofm:{sel_ofm}")
    if sel_ofm == OFM_BY_CONTENT:
        md_text_fixed = _fix_ocr_by_proc_whole(md_text, md_info, out_dir)
    elif sel_ofm == OFM_BY_PAGE:
        md_text_fixed = _fix_ocr_by_stiche_pages(md_text, md_info, out_dir)
    elif sel_ofm == OFM_BY_SKIP:
        md_text_fixed = md_text
    else:
        raise ValueError(f"unknown ofm: {sel_ofm}")

    fname_s1_md_name = os.path.basename(fname_output_s0_md).replace("_s0.md", "_s1.md")
    fname_output_s1_md = os.path.join(out_dir, fname_s1_md_name)
    with open(fname_output_s1_md, "w+") as f:
        f.write(md_text_fixed)

    logging.info(f"fname_output_s1_md: {fname_output_s1_md}")
    md_info["fname_output_s1_md"] = os.path.basename(fname_s1_md_name)
    md_info_path = save_md_info(out_dir, md_info)
    return md_info_path, md_info

if __name__ == "__main__":
    setup_logger_handlers()

    #ofm = None
    #md_info_path = "_work/ctn2md_exam5/info.json"

    ofm = OFM_BY_PAGE
    md_info_path = "_work/ctn2md_exam0/info.json"

    md_info_path, md_info = fix_ocr_content_by_gpt(md_info_path, ofm=ofm)
    print(md_info_path)
    rich.print(md_info)
