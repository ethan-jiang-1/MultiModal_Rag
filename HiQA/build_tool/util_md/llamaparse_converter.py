from dotenv import load_dotenv
import os
import sys
import logging
import rich
import random
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.build_tool.pdf2md.pdf2md import fix_ocr_self_correct_markdown


def _get_llamaparse():
    from llama_parse import LlamaParse

    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,  # 替换为您的 API 密钥
        result_type="markdown",  # 选择 "markdown" 格式输出
        #result_type="text",  # 选择 "markdown" 格式输出
        verbose=True,
        language="ch_sim",
        page_suffix="mark_page_separator_{page_number}"
    )
    return parser

def _dump_by_json_result(out_dir, json_result):
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
                md_full_content += md_page
                fname_page = f"{job_id}-content_p{ndx}.md"
                fname_page_md = os.path.join(out_dir, fname_page)
                with open(fname_page_md, "w", encoding="utf8") as f:
                    f.write(md_page)
                fnames_pages.append(fname_page)

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
                    md_imgs = "\n" + "\n".join(img_refs) + "\n"
                    md_full_content += md_imgs
    
    md_info = {"job_id": job_ids_set.pop(),
               "job_metadata": job_metadata,
               "fnames_imgs": fnames_imgs,
               "fnames_pages": fnames_pages,
               "fname_org_doc": file_paths_set.pop()}

    return md_full_content, md_info

def _dump_by_documents(out_dir, documents):
    md_full_content = ""
    for doc in documents:
        rich.print(doc)
        md_full_content += doc.text
    return md_full_content, {}


def fix_ocr_content(fname_output_md, out_dir):
    md_fixed_fname = os.path.basename(fname_output_md).replace(".md", "_fixed.md")
    fname_output_fixed_md = os.path.join(out_dir, md_fixed_fname)

    with open(fname_output_md, "r", encoding="utf8") as f:
        md_text = f.read()

    md_text_fixed = fix_ocr_self_correct_markdown(md_text)
    with open(fname_output_fixed_md, "w+") as f:
        f.write(md_text_fixed)

    return fname_output_fixed_md

def convert_doc_to_md_by_llamaparse(doc_pathname, out_dir):
    parser = _get_llamaparse()
    #logging.info(parser)

    basename = os.path.basename(doc_pathname)
    ext_name = basename.split(".")[-1]
    fname_md_name = basename.replace(f".{ext_name}", f"___{ext_name}.md")
    fname_output_md = os.path.join(out_dir, fname_md_name)

    documents = parser.load_data(doc_pathname)
    json_result = parser.get_json_result(doc_pathname) # noqa
    images = parser.get_images(json_result, out_dir)  # noqa
    #tables = parser.get_xlsx(json_result, out_dir)  # noqa

    with open(fname_output_md, "w+") as f: 
        if isinstance(json_result, list) and len(json_result) > 0:
            md_text, md_info = _dump_by_json_result(out_dir, json_result)
        else:
            md_text, md_info = _dump_by_documents(out_dir, documents)
        f.write(md_text)
    
    fname_output_fixed_md = fix_ocr_content(fname_output_md, out_dir)

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"orginal md:   {fname_output_md}")
    logging.info(f"ocr fixed md: {fname_output_fixed_md}")

    md_info["fname_orginal_md"] = os.path.basename(fname_output_md)
    md_info["fname_fixed_md"] = os.path.basename(fname_output_fixed_md)
    md_info["out_dir"] = out_dir
    fname_info_json = os.path.join(out_dir, "info.json")
    json_str = json.dumps(md_info, indent=4, ensure_ascii=False)
    with open(fname_info_json, 'w+', encoding='utf8') as f:
        f.write(json_str) 

    return fname_output_fixed_md, md_info


if __name__ == "__main__":
    #doc_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #doc_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    #doc_pathname = "datasrc/test/raw_docs/1. 座椅STO间隙 P1.pptx"
    #doc_pathname = "datasrc/test/raw_docs/管理者角色定位与认知课程大纲.docx"
    #doc_pathname = "datasrc/test/raw_docs/考勤修改统一规则.xlsx"
    doc_pathname = "datasrc/test/raw_docs/5. back panel 与环境匹配工程校核_P2.pptx"

    out_dir = f"_work/tmp_{random.randint(10,99)}"
    print(f"out_dir: {out_dir}")

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    fname_output_fixed_md, md_info = convert_doc_to_md_by_llamaparse(doc_pathname, out_dir)
    print(fname_output_fixed_md)
    rich.print(md_info)