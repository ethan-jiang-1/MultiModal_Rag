from dotenv import load_dotenv
import os
import sys
import logging
import rich
import random
#import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src.md_info_scan import analyze_scan_info

def _get_llamaparse():
    from llama_parse import LlamaParse

    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,  # 替换为您的 API 密钥
        result_type="markdown",  # 选择 "markdown" 格式输出
        #result_type="text",  # 选择 "markdown" 格式输出
        verbose=True,
        language="ch_sim",
        #page_suffix="mark_page_separator_{page_number}"
        invalidate_cache=True,
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

# TODO，ethan_enrich_md leave page info, line/total/all info in image tag to pickup to help TOC rebuild
def _dump_by_json_result(out_dir, json_result, md_info):
    os.makedirs(out_dir, exist_ok=True)
    md_full_content = ""
    job_ids_set = set()
    file_paths_set = set()
    job_metadata = {}
    fnames_imgs = []
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

        for ndx, page in enumerate(pages):
            rich.print(page)
            md_page = page.get("md", None)
            if md_page is not None:
                if len(md_full_content) != 0:
                    md_full_content += "\n"
                md_full_content += md_page

            md_imgs = ""
            images = page.get("images", None)
            if images is not None:
                img_refs = []
                for image in images:
                    path = image.get("path")
                    if path is not None and os.path.isfile(path):
                        basename = os.path.basename(path)
                        img_refs.append(f"![]({basename})")
                        fnames_imgs.append(basename)
                if len(img_refs) > 0:
                    md_imgs = "\n\n" + "\n".join(img_refs) + "\n"
                    md_full_content += md_imgs

                fname_page = _save_md_page(out_dir, job_id, ndx, md_page, md_imgs)
                fnames_pages.append(fname_page)
    
    info_extra = {"job_id": job_ids_set.pop(),
                  "job_metadata": job_metadata,
                  "fnames_imgs": fnames_imgs,
                  "fnames_pages": fnames_pages}
    
    md_info.update_info(info_extra)
    return md_full_content

# def _dump_by_documents(out_dir, documents, md_info):
#     md_full_content = ""
#     for doc in documents:
#         rich.print(doc)
#         md_full_content += doc.text
#     return md_full_content

def gen_md_llamaparse(doc_pathname, out_dir):
    parser = _get_llamaparse()
    #logging.info(parser)

    md_info = MdInfo(out_dir)
    md_info.set_doc_pathname(doc_pathname)

    documents = parser.load_data(doc_pathname)
    if documents is None or len(documents) == 0:
        raise ValueError(f"document is empty for {doc_pathname}")

    json_result = parser.get_json_result(doc_pathname) # noqa
    if json_result is None or len(json_result) == 0:
        raise ValueError(f"json_result is empty for {doc_pathname}")

    json_result0_pages = json_result[0].get("pages", None)
    scan_info = {}
    if json_result0_pages is not None:
        doc_type = doc_pathname.split(".")[-1].lower()
        scan_info = analyze_scan_info(json_result0_pages, doc_type)

    images = parser.get_images(json_result, out_dir)  # noqa
    #tables = parser.get_xlsx(json_result, out_dir)  # noqa

    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "w+") as f: 
        md_text = _dump_by_json_result(out_dir, json_result, md_info)
        f.write(md_text)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor="gen_md_llamaparse")

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")

    md_info["scan_info"] = scan_info
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    out_dir = f"_work/ctn2md_{random.randint(10,99)}"

    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    out_dir = "_work/ctn2md_40"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    #doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"
    #doc_pathname = "datasrc/exam/raw_docs/ChatGPT intimates a tantalizing future_compressed.pdf"

    os.makedirs(out_dir, exist_ok=True)
    print(f"out_dir: {out_dir}")

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_llamaparse(doc_pathname, out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)