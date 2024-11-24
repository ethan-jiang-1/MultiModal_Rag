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

def inject_aux_info_to_page(md_page, page_ndx, total_pages, md_info):
    """
    注入统计信息到 Markdown 文档标题行。
    :param md_page: str, 当前页面的 Markdown 内容
    :param page_ndx: int, 当前页码（从 0 开始计数）
    :param total_pages: int, 文档总页数
    :param md_info: dict, 包含整个文档的信息（例如标题等，暂未使用）
    :return: str, 注入统计信息后的 Markdown 文档内容
    """
    def count_chars(text):
        """
        统计文本中的字符数，忽略 Markdown 特殊符号和图片引用。
        """
        # 移除 Markdown 特殊符号和图片引用
        text = re.sub(r'[>#*_\-`~\[\]]', '', text)  # 去掉 Markdown 符号
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # 去掉图片引用
        text = re.sub(r'\s+', '', text)             # 去掉空白符
        return len(text)

    # 分割 Markdown 文档为行，并确定总行数
    lines = md_page.split('\n')
    total_lines = len(lines)

    # 使用正则提取标题和其内容范围
    sections = []
    current_section = {"title": None, "lines": []}

    for line in lines:
        if re.match(r'^#+\s', line):  # 如果是标题行
            # 如果当前有积累的标题范围，保存
            if current_section["title"]:
                sections.append(current_section)
            # 开始一个新的标题范围
            current_section = {"title": line, "lines": []}
        else:
            # 非标题行，归属于当前标题范围
            current_section["lines"].append(line)

    # 最后一个标题范围
    if current_section["title"]:
        sections.append(current_section)

    # 计算总字符数
    total_char_count = sum(
        count_chars(line) for line in lines
    )

    # 结果行列表
    result_lines = []
    for section in sections:
        title = section["title"]
        content_lines = section["lines"]
        content_char_count = sum(count_chars(line) for line in content_lines)

        # 注释信息
        line_number = lines.index(title) + 1
        injected_title = f"{title} <!-- PLW: Page:{page_ndx + 1}/{total_pages}, Line:{line_number}/{total_lines}, Chars:{content_char_count}/{total_char_count} -->"
        result_lines.append(injected_title)
        result_lines.extend(content_lines)

    return '\n'.join(result_lines)

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

        total_pages = len(pages)
        for page_ndx, page in enumerate(pages):
            rich.print(page)
            md_page = page.get("md", None)
            if md_page is not None:
                md_page_modified = inject_aux_info_to_page(md_page, page_ndx, total_pages, md_info)
                if len(md_page_modified) > 0:
                    if len(md_full_content) != 0:
                        md_full_content += "\n"
                    md_full_content += md_page_modified

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

                fname_page = _save_md_page(out_dir, job_id, page_ndx, md_page, md_imgs)
                fnames_pages.append(fname_page)
    
    info_extra = {"job_id": job_ids_set.pop(),
                  "job_metadata": job_metadata,
                  "fnames_imgs": fnames_imgs,
                  "fnames_pages": fnames_pages}
    
    md_info.update_info(info_extra)
    return md_full_content

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