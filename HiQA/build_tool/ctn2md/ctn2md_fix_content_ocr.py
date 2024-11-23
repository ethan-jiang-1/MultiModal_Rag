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
from HiQA.build_tool.utils_bt.llm_fix_ocr_md import fix_ocr_self_correct_markdown
from HiQA.build_tool.ctn2md.md_info_base import MdInfo
from HiQA.build_tool.ctn2md.md_info_scan import get_llm_ocr_fix_method, OFM_BY_CONTENT, OFM_BY_PAGE, OFM_BY_SKIP
from HiQA.utils.tokenizer import get_token_encoding

#TODO: check if we are able to make GPTo output more then 3*1024 token. and how
#MAX_OUTPUT_TOKEN = 8*1024
MAX_OUTPUT_TOKEN = 8*1024

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

def _fix_ocr_by_stiche_pages(md_text, md_info):
    fnames_pages = md_info.get_fnames_pages()
    if not fnames_pages:
        raise ValueError("fnames_pages is empty")
    
    md_text_fixed = ""
    out_dir = md_info.get_out_dir()
    question_num = 100
    total_pages = len(fnames_pages)
    logging.info(f"_fix_ocr_by_stiche_pages: total_pages: {total_pages}")
    model = "gpt-4o"
    if total_pages >= 6:
        model = "gpt-4o-mini"
    for ndx, fname_page in enumerate(fnames_pages):
        pathname = os.path.join(out_dir, fname_page)
        with open(pathname, 'r', encoding='utf8') as f:
            md_page = f.read()
        doc_type = md_info.get_doc_type()
        md_page_fixed = fix_ocr_self_correct_markdown(md_page, doc_type, model=model, question_num=question_num) 
        md_text_fixed += md_page_fixed + "\n"
        question_num += 1

    return md_text_fixed      

def _fix_ocr_by_proc_whole(md_text, md_info):
    doc_type = md_info.get_doc_type()
    md_text_fixed = fix_ocr_self_correct_markdown(md_text, doc_type)  
    return md_text_fixed

def fix_ocr_content_by_gpt(md_info_path, src_step_num=None, ofm=None):
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"no {pathname_src_step_md} and {pathname_dst_step_md}")

    with open(pathname_src_step_md, "r", encoding="utf8") as f:
        md_text = f.read()

    total_tokens = _calculate_tokens_large_text(md_text, stop_check_over_max=True)
    is_tokens_over_llm_output = (total_tokens > MAX_OUTPUT_TOKEN)
    ofm_reason = ""
    if ofm is None:
        md_info["is_tokens_over_llm_output"] = is_tokens_over_llm_output
        ofm, ofm_reason = get_llm_ocr_fix_method(md_info)

    logging.info(f"OFM: ofm:{ofm}")
    if ofm == OFM_BY_CONTENT:
        if total_tokens > MAX_OUTPUT_TOKEN:
            ofm = OFM_BY_PAGE
            ofm_reason += ":>llm_tklimit"
            md_text_fixed = _fix_ocr_by_stiche_pages(md_text, md_info) 
        else:
            md_text_fixed = _fix_ocr_by_proc_whole(md_text, md_info)
    elif ofm == OFM_BY_PAGE:
        md_text_fixed = _fix_ocr_by_stiche_pages(md_text, md_info)
    elif ofm == OFM_BY_SKIP:
        md_text_fixed = md_text
    else:
        raise ValueError(f"unknown ofm: {ofm}")

    logging.warning(f"fix_ocr_content_by_gpt: pathname_dst_step_md: {pathname_dst_step_md}")
    with open(pathname_dst_step_md, "w+") as f:
        f.write(md_text_fixed)
    
    md_info.add_step_into_md_info_streams(pathname_dst_step_md, actor=f"fix_ocr_content_by_gpt:{ofm}:{ofm_reason}")
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    ofm = None
    src_step_num = 0
    #md_info_path = "_work/ctn2md_exam5/info.json"

    #ofm = OFM_BY_PAGE
    #md_info_path = "_work/ctn2md_stream1/info.json"

    md_info_path = "_work/ctn2md_40/_info.json"

    md_info_path = fix_ocr_content_by_gpt(md_info_path, ofm=ofm, src_step_num=src_step_num)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)
