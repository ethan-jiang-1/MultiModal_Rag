
from typing import List, Tuple
from dotenv import load_dotenv
import sys
import os
#import logging
import rich
import re
from qdrant_client.http.models import Filter, FieldCondition

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.query.query_bsae import ScoredSection
from mrag_vdb.common.vdb_base import REF_PATH
from mrag_vdb.common.vdb_base import VDB_PATH
from mrag_vdb.utils.util_file import get_root_dir
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.vdb_base import QdrantClientContextManager
from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo

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

def _construct_ref_imgs_map(ref_img_fnames: List[str], ref_img_titles: List[str], ref_section: ScoredSection):
    ref_imgs_map = {}
    for ref_img_fname, ref_img_title in zip(ref_img_fnames, ref_img_titles):
        if ref_img_fname not in ref_imgs_map:
            ref_img_pname = _get_ref_pname(ref_section.collection_name, ref_section.doc_unique_id, ref_img_fname)
            ref_imgs_map[ref_img_fname] = (ref_img_pname, ref_img_title)

    return ref_imgs_map

def _check_if_imgs_are_related_to_qa(query: str, answer: str, context: str, ref_img_titles: List[str]):
    # using context, query and answer to check if ref from slibing are good fit images
    ref_img_titles_relevance_scores = [0.0 for item in ref_img_titles]
    return ref_img_titles_relevance_scores

def _find_ref_imgs_map_from_nearset_silbings(query: str, answer: str, slibling_move: int, ref_section: ScoredSection):
    """
    根据兄弟章节的位置找到相关的图片，并过滤符合条件的图片（相关性 > 2.0）。
    
    参数:
        query (str): 查询内容。
        answer (str): 答案内容。
        slibling_move (int): 移动的方向：-1 表示上一个兄弟章节，+1 表示下一个兄弟章节。
        ref_section (ScoredSection): 当前章节对象。
    
    返回:
        dict: 过滤后的图片信息映射，键为图片文件名，值为图片路径和标题。
    """
    # 获取当前章节的 sec_id 和 parent_sec_id
    parent_sec_id = ref_section.parent_sec_id
    current_sec_id = ref_section.sec_id

    # 通过 sec_id 来确定兄弟章节的位置。假设我们有方法来查询兄弟章节
    sibling_sec_id = _get_sibling_sec_id(parent_sec_id, current_sec_id, slibling_move)

    if sibling_sec_id is None:
        # 没有找到兄弟章节，返回空字典
        return {}

    # 查找兄弟章节的内容（我们假设这里有方法可以根据 sec_id 获取章节）
    sibling_section = _get_section_by_sec_id(sibling_sec_id, ref_section.doc_unique_id, ref_section.collection_name)
    if not sibling_section:
        return {}

    # 扫描兄弟章节中的图片文件和标题
    ref_img_fnames, ref_img_titles = _scan_markdown_for_ref_imgs(sibling_section.content)
    
    if len(ref_img_fnames) == 0:
        # 如果没有图片，返回空字典
        return {}

    # 构建图片映射
    ref_imgs_map = _construct_ref_imgs_map(ref_img_fnames, ref_img_titles, sibling_section)

    # 过滤掉相关性评分小于 2.0 的图片
    filtered_ref_imgs_map = {}
    for img_fname, (img_pname, img_title) in ref_imgs_map.items():
        relevance_score = _check_if_imgs_are_related_to_qa(query, answer, sibling_section.content, [img_title])
        
        if relevance_score[0] > 2.0:  # 相关性评分大于 2.0
            filtered_ref_imgs_map[img_fname] = (img_pname, img_title)

    return filtered_ref_imgs_map


def _get_sibling_sec_id(parent_sec_id: str, current_sec_id: str, slibling_move: int) -> str:
    """
    通过当前章节的 `parent_sec_id` 和 `sec_id`，找到前一个或后一个兄弟章节的 `sec_id`。
    
    参数:
        parent_sec_id (str): 父章节的 id。
        current_sec_id (str): 当前章节的 id。
        slibling_move (int): -1 表示找前一个兄弟章节，+1 表示找下一个兄弟章节。
    
    返回:
        str: 兄弟章节的 `sec_id`。
    """
    # 这里可以通过一些规则来计算兄弟章节的 `sec_id`
    # 比如，我们可以通过 `sec_id` 的层级结构来推算
    # 假设 sec_id 类似 1.1, 1.2, 1.3 这种格式，可以根据数值范围来调整
    sec_ids = current_sec_id.split(".")
    if slibling_move == 1:
        # 下一个兄弟章节
        sec_ids[-1] = str(int(sec_ids[-1]) + 1)
    elif slibling_move == -1:
        # 上一个兄弟章节
        sec_ids[-1] = str(int(sec_ids[-1]) - 1)

    return ".".join(sec_ids)


def _get_section_by_sec_id(sec_id: str, doc_unique_id: str, collection_name: str) -> ScoredSection:
    """
    根据 sec_id 获取章节的详细信息。
    使用 Qdrant 客户端进行查询，返回一个 ScoredSection 对象。

    参数:
        sec_id (str): 章节 id。
        collection_name (str): 集合的名称（例如文档的名称）。
    
    返回:
        ScoredSection: 对应的章节对象。
    """
    with QdrantClientContextManager(path=VDB_PATH) as client:
        filter_query = Filter(
            must=[
                FieldCondition(key="sec_id", match={"value": sec_id}),
                FieldCondition(key="doc_unique_id", match={"value": doc_unique_id})
            ]
        )

        # 执行查询，limit=1 只获取一个匹配项
        result = client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_query,
            limit=1,
            with_vectors=False  # 假设这里不需要向量数据
        )

        # 如果有查询结果且结果包含数据点
        if result and result[0]:
            # 假设 result[0][0] 是我们需要的章节数据点
            point = result[0][0]
            
            # 获取 payload 中的 ChunkedSectionInfo 信息
            csi = ChunkedSectionInfo(**point.payload)
            
            # 构造 ScoredSection 对象，如果缺少某些字段使用默认值
            return ScoredSection(
                score=0.0,  # 默认值
                score_rrf=0.0,  # 默认值
                sec_id=sec_id,
                parent_sec_id=csi.parent_sec_id,
                heading=csi.heading,
                level=csi.level,
                desc=csi.desc,
                doc_unique_id=csi.doc_unique_id,
                doc_title=csi.doc_title,
                fname_org_doc=csi.fname_org_doc,
                content=csi.content,
                payloads=point.payload,  # 使用 payload 作为 ScoredSection 的 payload
                knowledge_snippet=None,  # 默认值，视需求而定
                collection_name=collection_name,
            )

    # 如果没有查询到结果，返回 None 或者抛出异常
    return None

def _find_ref_imgs_map(query: str, answer: str, ref_section: ScoredSection):
    ref_img_fnames, ref_img_titles = _scan_markdown_for_ref_imgs(ref_section.content)
    if len(ref_img_fnames) > 0: 
        return _construct_ref_imgs_map(ref_img_fnames, ref_img_titles, ref_section)
    
    ref_imgs_map = _find_ref_imgs_map_from_nearset_silbings(query, answer, 1, ref_section) # after
    if not ref_imgs_map:
        ref_imgs_map = _find_ref_imgs_map_from_nearset_silbings(query, answer, -1, ref_section) # before
    return ref_imgs_map


def search_for_file_refs(query: str, resp: dict, scored_sections_reranked:List[ScoredSection]):
    refs_info = {}
    answer = resp.get("simple_answer", "")
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
                refs_info[ref_doc_fname]["ref_imgs_map"] = _find_ref_imgs_map(query, answer, ref_section)

    rich.print(refs_info)
    return refs_info

if __name__ == "__main__":
    from mrag_vdb.query.query_bsae import ScoredSection
    from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection
    from mrag_vdb.query.query2section_reranked import query2sortedsections_reranked
    from mrag_vdb.query.query2knowledge import form_knowledge_sections, knowledge_retrieve

    setup_logger_handlers()
    
    #query_str = "神经网络 中央处理器"
    #query_str = "椅背板与旁侧板的保留运动间隙是多少"
    #query_str = "靠背最后位置时与侧板翻边的运动间隙是多少"
    query_str = "法规要求的前后排座椅距离是多少"
    
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
