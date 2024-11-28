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

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.src.md_process_plc import inject_plc_comment_to_page
from ctn2md.gen_lp.lp_base import dump_images_ref_by_page, save_md_page
from ctn2md.gen_lp.lp_unique_job import n2u_restore_unique_name_premium

def _get_llamaparse_premium(md_info):
    from llama_parse import LlamaParse
    from llama_parse.utils import Language

    language = md_info.get_md_control("mctl_lp_langauge", Language.SIMPLIFIED_CHINESE)
    take_screenshot = False  # md_info.get_md_control("mctl_lp_take_screenshot", False)
    disable_ocr = False  # md_info.get_md_control("mctl_lp_disable_ocr", False)

    target_pages = md_info.get_md_control("mctl_lp_premium_pages", None)
    if target_pages is None or len(target_pages) == 0:
        raise ValueError("no parser in premium_mode if mctl_lp_premium_pages is None")

    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,  # 替换为您的 API 密钥
        result_type="markdown",  # 选择 "markdown" 格式输出
        verbose=True,
        language=language,  # "ch_sim",
        #page_suffix="mark_page_separator_{page_number}"
        invalidate_cache=True,
        check_interval=3,
        max_timeout=30*60,
        take_screenshot=take_screenshot,
        disable_ocr=disable_ocr,
        premium_mode=True,
        target_pages=target_pages
    )
    return parser

def _dump_preminum_md_page_content_from_lp_json_result(json_result, md_info):
    out_dir = md_info.get_out_dir()
    job_ids_set = set()
    file_paths_set = set()
    fnames_pages = []
    for node in json_result:
        job_id = node.get("job_id", None)
        job_ids_set.add(job_id)
        file_path = node.get("file_path", None)
        file_paths_set.add(file_path)

        logging.info(f"job_id: {job_id}")
        pages = node.get("pages", None)
        if pages is None:
            continue

        total_pages = len(md_info[MIFN.FNAMES_PAGES])
        for page_ndx, page in enumerate(pages):
            rich.print(page)
            page_no = page.get("page", None)
            md_page = page.get("md", None)
            if md_page is not None:
                md_page_modified = inject_plc_comment_to_page(md_page, page_no, total_pages, md_info)

                md_imgs = dump_images_ref_by_page(page)

                fname_page = save_md_page(out_dir, job_id, page_no, md_page_modified, md_imgs)
                fnames_pages.append(fname_page)
            else:
                raise ValueError("what?")
    
    md_info[MIFN.FNAMES_P_PAGES] = fnames_pages
    cur_job_id = job_ids_set.pop()
    return cur_job_id

def _dump_tables(parser, json_result, md_info):
    out_dir = md_info.get_out_dir()
    tables = parser.get_xlsx(json_result, out_dir)
    fnames_tbls = [os.path.basename(item["path"]) for item in tables]
    md_info[MIFN.FNAMES_P_TBLS] = fnames_tbls 

def gen_preminum_pages(md_info):
    doc_pathname = md_info.get_doc_pathname()

    parser = _get_llamaparse_premium(md_info)

    documents = parser.load_data(doc_pathname)
    if documents is None or len(documents) == 0:
        raise ValueError(f"document is empty for {doc_pathname}")

    json_result = parser.get_json_result(doc_pathname)
    if json_result is None or len(json_result) == 0:
        raise ValueError(f"json_result is empty for {doc_pathname}")

    _dump_tables(parser, json_result, md_info)
    cur_job_id = _dump_preminum_md_page_content_from_lp_json_result(json_result, md_info)
    n2u_restore_unique_name_premium(md_info, cur_job_id)
    return json_result


if __name__ == "__main__":
    setup_logger_handlers()
    
    md_info_path = "_work/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    md_info = MdInfo(md_info_path)

    ret = gen_preminum_pages(md_info)
    rich.print(ret)