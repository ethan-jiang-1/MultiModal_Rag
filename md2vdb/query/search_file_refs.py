from typing import List, Tuple
from dotenv import load_dotenv
import sys
import os
#import logging
import rich
import re

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.query.query_bsae import ScoredSection
from md2vdb.common.vdb_base import REF_PATH
from md2vdb.utils.util_file import get_root_dir
from md2vdb.utils.util_logging import setup_logger_handlers


def _get_ref_pname(collection_name:str, unique_doc_id:str, fname:str):
    dir_root = get_root_dir()
    pathname = os.path.join(dir_root, REF_PATH, f"{collection_name}_{unique_doc_id}", fname)
    return pathname

def _scan_markdown_for_ref_imgs(md_content: str) -> Tuple[List[str], List[str]]:
    """
    扫描 Markdown 内容以提取引用的图片文件名和标题。

    参数:
        md_content (str): Markdown 格式的内容。
    
    返回:
        Tuple[List[str], List[str]]: 
            - ref_img_fnames: 图片文件名的列表。
            - ref_img_titles: 图片标题的列表。
    """
    # 用正则表达式匹配 Markdown 图片语法
    # 格式: ![alt text](image_url "optional title")
    img_pattern = r'!\[.*?\]\((.*?)(?: "(.*?)")?\)'
    matches = re.findall(img_pattern, md_content)

    # 提取文件名和标题
    ref_img_fnames = []
    ref_img_titles = []

    for match in matches:
        image_url = match[0]
        image_title = match[1] if len(match) > 1 and match[1] else ""

        # 只获取文件名（去除路径部分）
        img_fname = image_url.split("/")[-1] if "/" in image_url else image_url
        ref_img_fnames.append(img_fname)
        ref_img_titles.append(image_title)

    return ref_img_fnames, ref_img_titles

def _find_ref_imgs_map(ref_section: ScoredSection):
    md_content = ref_section.content
    ref_img_fnames, ref_img_titles = _scan_markdown_for_ref_imgs(md_content)

    ref_imgs_map = {}
    for ref_img_fname, ref_img_title in zip(ref_img_fnames, ref_img_titles):
        if ref_img_fname not in ref_imgs_map:
            ref_img_pname = _get_ref_pname(ref_section.collection_name, ref_section.doc_unique_id, ref_img_fname)
            ref_imgs_map[ref_img_fname] = (ref_img_pname, ref_img_title)

    return ref_imgs_map

def search_for_file_refs(query: str, resp: dict, scored_sections_reranked:List[ScoredSection]):
    refs_info = {}
    detailed_refernces = resp.get("detailed_references", None)
    if detailed_refernces is not None:
        for ref in detailed_refernces:
            snippet_id = ref.get("snippet_id", None)
            if snippet_id is None:
                continue
            snippet_id = int(snippet_id) - 1
            if not (snippet_id >= 0 and snippet_id < len(scored_sections_reranked)):
                continue

            ref_section = scored_sections_reranked[snippet_id]
            rich.print(ref_section)

            ref_doc_fname = ref_section.fname_org_doc
            ref_doc_pname = _get_ref_pname(ref_section.collection_name, ref_section.doc_unique_id, ref_doc_fname)
            ref_doc_title = ref_section.doc_title

            if ref_doc_fname not in refs_info:
                refs_info[ref_doc_fname] = {}
                refs_info[ref_doc_fname]["ref_doc_tuple"] = (ref_doc_pname, ref_doc_title) 
                refs_info[ref_doc_fname]["ref_imgs_map"] = _find_ref_imgs_map(ref_section)


    rich.print(refs_info)
    return refs_info

if __name__ == "__main__":
    from md2vdb.query.query_bsae import ScoredSection
    from md2vdb.query.query2section_raw import query2section_raw_on_multiple_collection
    from md2vdb.query.query2section_reranked import query2sortedsections_reranked
    from md2vdb.query.query2knowledge import form_knowledge_sections, knowledge_retrieve

    setup_logger_handlers()
    
    #query_str = "神经网络 中央处理器"
    query_str = "椅背板与旁侧板的保留运动间隙是多少"
    collection_names = ["mrag"]
    limit = 10

    query = query_str

    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query, limit=limit)

    scored_sections_reranked = query2sortedsections_reranked(query, scored_sections_raw)

    knowledge = form_knowledge_sections(scored_sections_reranked)

    resp = knowledge_retrieve(query, knowledge, scored_sections_reranked)

    refs_info = search_for_file_refs(query, resp, scored_sections_reranked)
    print()
    rich.print(refs_info)
