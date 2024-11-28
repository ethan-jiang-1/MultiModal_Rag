from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
import re
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.src.llamaparse_result_revisit import post_scan_llamaparse_result
from ctn2md.src.md_process_plc import inject_plc_comment_to_page


def _get_llamaparse(md_info):
    from llama_parse import LlamaParse
    from llama_parse.utils import Language

    language = md_info.get_md_control("mctl_lp_langauge", Language.SIMPLIFIED_CHINESE)
    take_screenshot = md_info.get_md_control("mctl_take_screenshot", False)
    disable_ocr = md_info.get_md_control("mctl_lp_disable_ocr", False)

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
    )
    return parser

def _save_md_page(out_dir, job_id, ndx, md_page, md_imgs):
    try:
        md_page_all = md_page + md_imgs
        fname_page = f"{job_id}-content_p{ndx}.md"
        fname_page_md = os.path.join(out_dir, fname_page)
        with open(fname_page_md, "w", encoding="utf8") as f:
            f.write(md_page_all)
        return fname_page
    except Exception as ex:
        logging.exception(ex)
    return None

def _n2u_replace_fnames(md_info, mifn_fnames, unique_job_id, new_job_id):
    out_dir = md_info.get_out_dir()
    changed = 0
    md_info_mifn_fnames = md_info[mifn_fnames]
    for ndx, new_fname in enumerate(md_info_mifn_fnames):
        unique_fname = new_fname.replace(new_job_id, unique_job_id)
        if unique_fname != new_fname:

            src_fname = os.path.join(out_dir, new_fname)
            dst_fname = os.path.join(out_dir, unique_fname)
            shutil.move(src_fname, dst_fname)

            md_info_mifn_fnames[ndx] = unique_fname
            changed += 1
    return changed

def _n2u_update_md_content(md_info, pathname_md, unique_job_id, new_job_id):
    with open(pathname_md, "r") as f: 
        md_text = f.read()

    with open(pathname_md, "w+") as f: 
        md_text_new = md_text.replace(new_job_id, unique_job_id)
        f.write(md_text_new)

def _n2u_stick_with_old_names(md_info, unique_job_id, new_job_id):
    if unique_job_id == new_job_id:
        return 
    
    out_dir = md_info.get_out_dir()
    _n2u_replace_fnames(md_info, MIFN.FNAMES_PAGES, unique_job_id, new_job_id)
    _n2u_replace_fnames(md_info, MIFN.FNAMES_IMGS, unique_job_id, new_job_id)
    _n2u_replace_fnames(md_info, MIFN.FNAMES_TBLS, unique_job_id, new_job_id)

    for fname_md_page in md_info[MIFN.FNAMES_PAGES]:
        pathname_page = os.path.join(out_dir, fname_md_page)
        _n2u_update_md_content(md_info, pathname_page, unique_job_id, new_job_id)

    pathname_step0 = md_info.name_step_pathname(0)
    _n2u_update_md_content(md_info, pathname_step0, unique_job_id, new_job_id)

def _n2u_restore_unique_name(md_info):
    cur_job_id = md_info.get(MIFN.LP_CUR_JOB_ID)
    unique_job_id = md_info.get_unique_job_id()
    _n2u_stick_with_old_names(md_info, unique_job_id, cur_job_id)

def _dump_images_ref_by_page(page):
    md_imgs = ""
    images = page.get("images", None)
    if images is not None:
        img_refs = []
        for image in images:
            path = image.get("path")
            if path is not None and os.path.isfile(path):
                basename = os.path.basename(path)
                img_refs.append(f"![]({basename})")
            else:
                logging.warning(f"image file {path} not found.")
        if len(img_refs) > 0:
            md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
    return md_imgs 

def _dump_md_content_from_lp_json_result(out_dir, json_result, md_info):
    os.makedirs(out_dir, exist_ok=True)
    md_full_content = ""
    job_ids_set = set()
    file_paths_set = set()
    job_metadata = {}
    fnames_pages = []
    for node in json_result:
        job_id = node.get("job_id", None)
        job_ids_set.add(job_id)
        file_path = node.get("file_path", None)
        file_paths_set.add(file_path)
        job_metadata = node.get("job_metadata", {})

        logging.info(f"job_id: {job_id}")
        pages = node.get("pages", None)
        if pages is None:
            continue

        total_pages = len(pages)
        for page_ndx, page in enumerate(pages):
            rich.print(page)
            md_page = page.get("md", None)
            if md_page is not None:
                md_page_modified = inject_plc_comment_to_page(md_page, page_ndx, total_pages, md_info)
                if len(md_page_modified) > 0:
                    if len(md_full_content) != 0:
                        md_full_content += "\n"
                    md_full_content += md_page_modified

            md_imgs = _dump_images_ref_by_page(page)
            md_full_content += md_imgs

            fname_page = _save_md_page(out_dir, job_id, page_ndx, md_page_modified, md_imgs)
            fnames_pages.append(fname_page)
    
    cur_job_id = job_ids_set.pop()
    md_info[MIFN.LP_CUR_JOB_ID] = cur_job_id
    md_info[MIFN.LP_CUR_JOB_METADATA] = job_metadata
    md_info[MIFN.FNAMES_PAGES] = fnames_pages
    if MIFN.LP_JOB_ID_HISTORY not in md_info:
        md_info[MIFN.LP_JOB_ID_HISTORY] = []
    md_info[MIFN.LP_JOB_ID_HISTORY].append(cur_job_id)
    md_info.save()
    return md_full_content

def _remove_misc_files(md_info):
    """
    清理指定目录及其子目录下，以特定规则命名的文件：
    1. 以类似 UUID 前缀命名的文件。
    2. 以 xcs0000_（四位数字）前缀命名的 .md 文件。

    Args:
        md_info: 提供输出目录的对象，需实现 get_out_dir 方法。
    """
    # 获取输出目录
    out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    os.makedirs(aux_dir, exist_ok=True)

    if not out_dir or not os.path.exists(out_dir):
        print(f"目录不存在或无效: {out_dir}")
        return

    # 正则模式
    uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    xcs_pattern = re.compile(r"^xcs\d{4}_.*\.md$")  # 匹配 xcs0000_ 开头的 .md 文件

    # 遍历目录及其子目录
    for root, _, files in os.walk(out_dir):
        files = sorted(files)
        for file_name in files:
            src_path = os.path.join(root, file_name)
            if uuid_pattern.match(file_name) or xcs_pattern.match(file_name):  # 匹配任意一个模式
                try:
                    dst_path = os.path.join(aux_dir, os.path.basename(src_path))
                    shutil.move(src_path, dst_path)
                except Exception as e:
                    logging.exception(f"删除失败: {src_path}, 错误: {e}")

def _dump_images(parser, json_result, md_info):
    out_dir = md_info.get_out_dir()
    images = parser.get_images(json_result, out_dir)
    fnames_imgs = [os.path.basename(item["path"]) for item in images if item["name"].startswith("img_")]
    fnames_snps = [os.path.basename(item["path"]) for item in images if item["name"].statswith("pages_")]
    md_info[MIFN.FNAMES_IMGS] = fnames_imgs
    md_info[MIFN.FNAMES_SNPS] = fnames_snps

def _dump_tables(parser, json_result, md_info):
    out_dir = md_info.get_out_dir()
    tables = parser.get_xlsx(json_result, out_dir)
    fnames_tbls = [os.path.basename(item["path"]) for item in tables]
    md_info[MIFN.FNAMES_TBLS] = fnames_tbls    

def gen_md_llamaparse(doc_pathname, out_dir):
    #logging.info(parser)

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine("llamaparse:lp")
    md_info.set_doc_pathname(doc_pathname)

    parser = _get_llamaparse(md_info)

    documents = parser.load_data(doc_pathname)
    if documents is None or len(documents) == 0:
        raise ValueError(f"document is empty for {doc_pathname}")

    json_result = parser.get_json_result(doc_pathname)
    if json_result is None or len(json_result) == 0:
        raise ValueError(f"json_result is empty for {doc_pathname}")

    _remove_misc_files(md_info)
    _dump_images(parser, json_result, md_info)
    _dump_tables(parser, json_result, md_info)
 
    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "w+") as f: 
        md_text = _dump_md_content_from_lp_json_result(out_dir, json_result, md_info)
        f.write(md_text)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor="gen_md_llamaparse")

    md_info.save()
    _n2u_restore_unique_name(md_info)
    md_info.save()

    post_scan_llamaparse_result(md_info, json_result=json_result)

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)