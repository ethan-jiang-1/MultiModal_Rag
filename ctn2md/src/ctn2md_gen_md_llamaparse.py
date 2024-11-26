from dotenv import load_dotenv
import os
import sys
import logging
import rich
import random
import re

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MDFN
from ctn2md.src.md_info_scan import analyze_lp_scan_info
from ctn2md.src.md_process_plc import inject_plc_comment_to_page

def _get_llamaparse():
    from llama_parse import LlamaParse
    from llama_parse.utils import Language

    #TODO: ethan_llamaparse parameters
    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,  # 替换为您的 API 密钥
        result_type="markdown",  # 选择 "markdown" 格式输出
        verbose=True,
        language=Language.SIMPLIFIED_CHINESE,  # "ch_sim",
        #page_suffix="mark_page_separator_{page_number}"
        invalidate_cache=True,
        check_interval=3,
        max_timeout=30*60,
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
    
    info_extra = {MDFN.LP_JOB_ID: job_ids_set.pop(),
                  MDFN.LP_JOB_METADATA: job_metadata,
                  MDFN.FNAMES_PAGES: fnames_pages}
    
    md_info.update_info(info_extra)
    return md_full_content

def _clean_misc_files(md_info):
    """
    清理指定目录及其子目录下，以特定规则命名的文件：
    1. 以类似 UUID 前缀命名的文件。
    2. 以 xcs0000_（四位数字）前缀命名的 .md 文件。

    Args:
        md_info: 提供输出目录的对象，需实现 get_out_dir 方法。
    """
    # 获取输出目录
    out_dir = md_info.get_out_dir()

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
            file_path = os.path.join(root, file_name)
            if uuid_pattern.match(file_name) or xcs_pattern.match(file_name):  # 匹配任意一个模式
                try:
                    os.remove(file_path)
                    logging.info(f"已删除: {file_path}")
                except Exception as e:
                    logging.exception(f"删除失败: {file_path}, 错误: {e}")

def _dump_page_scan_info(json_result, md_info):
    if json_result is not None and len(json_result) > 0:
        json_result0_pages = json_result[0].get("pages", None)
        lp_scan_info = {}
        if json_result0_pages is not None:
            doc_pathname = md_info.get_doc_pathname()
            doc_type = doc_pathname.split(".")[-1].lower()
            lp_scan_info = analyze_lp_scan_info(json_result0_pages, doc_type)
        md_info[MDFN.LP_SCAN_INFO] = lp_scan_info

def _dump_images(parser, json_result, md_info):
    out_dir = md_info.get_out_dir()
    images = parser.get_images(json_result, out_dir)
    fnames_imgs = [os.path.basename(item["path"]) for item in images]
    md_info[MDFN.FNAMES_IMGS] = fnames_imgs

def _dump_tables(parser, json_result, md_info):
    out_dir = md_info.get_out_dir()
    tables = parser.get_xlsx(json_result, out_dir)
    fnames_tbls = [os.path.basename(item["path"]) for item in tables]
    md_info[MDFN.FNAMES_TBLS] = fnames_tbls    

def gen_md_llamaparse(doc_pathname, out_dir):
    parser = _get_llamaparse()
    #logging.info(parser)

    md_info = MdInfo(out_dir)
    md_info.set_gen_engine("llamaparse:lp")
    md_info.set_doc_pathname(doc_pathname)

    documents = parser.load_data(doc_pathname)
    if documents is None or len(documents) == 0:
        raise ValueError(f"document is empty for {doc_pathname}")

    json_result = parser.get_json_result(doc_pathname)
    if json_result is None or len(json_result) == 0:
        raise ValueError(f"json_result is empty for {doc_pathname}")

    _clean_misc_files(md_info)
    _dump_images(parser, json_result, md_info)
    _dump_tables(parser, json_result, md_info)
    _dump_page_scan_info(json_result, md_info)

    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "w+") as f: 
        md_text = _dump_md_content_from_lp_json_result(out_dir, json_result, md_info)
        f.write(md_text)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor="gen_md_llamaparse")

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    out_dir = f"_work/ctn2md_{random.randint(10,99)}"

    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/深度学习在视电阻率快速反演中的研究.pdf"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)