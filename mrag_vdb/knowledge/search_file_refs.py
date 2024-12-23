
from typing import List, Optional, Tuple
from dotenv import load_dotenv
import sys
import os
import logging
import rich
import re
from qdrant_client.http.models import Filter, FieldCondition

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.common.vdb_base import REF_PATH
from mrag_vdb.common.vdb_base import VDB_PATH
from mrag_vdb.utils.util_file import get_root_dir
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.vdb_base import QdrantClientContextManager
from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo
from mrag_vdb.utils_llm.llm_image_relevance_gpt import check_img_relevance_by_gpt

MIN_IMG_RELEVANCE_SCORE = 2.0

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

def _construct_ref_imgs_map(ref_img_fnames: List[str], ref_img_titles: List[str], ref_section: ScoredRecoveredSection):
    ref_imgs_map = {}
    for ref_img_fname, ref_img_title in zip(ref_img_fnames, ref_img_titles):
        if ref_img_fname not in ref_imgs_map:
            ref_img_pname = _get_ref_pname(ref_section.collection_name, ref_section.doc_unique_id, ref_img_fname)
            ref_imgs_map[ref_img_fname] = (ref_img_pname, ref_img_title)

    return ref_imgs_map


def _get_section_by_seq_no(collection_name: str, doc_unique_id: str, seq_no: int) -> Optional[ScoredRecoveredSection]:
    """
    根据 doc_unique_id + sec_seq_no 直接查询 Qdrant,
    返回对应的 ScoredSection（若无则返回 None）。
    """
    with QdrantClientContextManager(path=VDB_PATH) as client:
        filter_query = Filter(
            must=[
                FieldCondition(key="doc_unique_id", match={"value": doc_unique_id}),
                FieldCondition(key="sec_seq_no", match={"value": seq_no}),
            ]
        )
        result = client.scroll(
            collection_name=collection_name,
            scroll_filter=filter_query,
            limit=1,
            with_vectors=False
        )

        if result and result[0]:
            point = result[0][0]
            csi = ChunkedSectionInfo(**point.payload)
            return ScoredRecoveredSection(
                score=0.0,
                score_rrf=0.0,
                sec_id=csi.sec_id,
                parent_sec_id=csi.parent_sec_id,
                heading=csi.heading,
                level=csi.level,
                desc=csi.desc,
                doc_unique_id=csi.doc_unique_id,
                doc_title=csi.doc_title,
                doc_ctn_type=csi.doc_ctn_type,
                fname_org_doc=csi.fname_org_doc,
                content=csi.content,
                sec_seq_no=csi.sec_seq_no,
                payloads=point.payload,
                knowledge_snippet=None,
                collection_name=collection_name,
            )
    return None

def _is_toc_relevant(ref_section: ScoredRecoveredSection, neighbor_section: ScoredRecoveredSection, offset: int) -> bool:
    """
    判断 neighbor_section 是否在 TOC 上和 ref_section 存在
    - 同级（Sibling）
    - 父级（Parent）
    - 子级（Child）
    这三种关系。
    
    offset < 0 => 可能是前面的 chunk（Sibling 或 Parent）
    offset > 0 => 可能是后面的 chunk（Sibling 或 Child）
    """
    # 同级 (Sibling)
    if neighbor_section.parent_sec_id == ref_section.parent_sec_id:
        return True

    # 前面 => 也可能是父级
    if offset < 0:
        # 如果 neighbor_section 就是 ref_section 的 parent
        if neighbor_section.sec_id == ref_section.parent_sec_id:
            return True

    # 后面 => 也可能是子级
    if offset > 0:
        # 如果 neighbor_section 的 parent 就是 ref_section
        if neighbor_section.parent_sec_id == ref_section.sec_id:
            return True

    return False

def _find_ref_imgs_map_lqcut(query: str, answer: str, ref_section: ScoredRecoveredSection) -> dict:
    """
    只在前/后几个相邻的 sec_seq_no 中寻找那些 TOC 上
    属于 Sibling/Parent/Child 的章节，以尝试获取图片引用。
    """
    # 可以根据需要扩展搜索范围，比如 [-2, -1, +1, +2]
    near_seq_offsets = [-1, +1]  

    found_map = {}
    for offset in near_seq_offsets:
        neighbor_seq_no = ref_section.sec_seq_no + offset
        neighbor_section = _get_section_by_seq_no(
            ref_section.collection_name,
            ref_section.doc_unique_id,
            neighbor_seq_no
        )
        if not neighbor_section:
            continue

        # 先判断 TOC 关系（Sibling / Parent / Child）
        if not _is_toc_relevant(ref_section, neighbor_section, offset):
            # 如果不符合你列出的 3 种情况，跳过
            continue

        # 如果 TOC 相关，再扫描图片
        n_img_fnames, n_img_titles = _scan_markdown_for_ref_imgs(neighbor_section.content)
        if n_img_fnames:
            candidate_map = _construct_ref_imgs_map(n_img_fnames, n_img_titles, neighbor_section)
            
            found_map.update(candidate_map)

    return found_map

def _is_ctn_gen_by_high_quality_parse_engine(ref_section: ScoredRecoveredSection) -> bool:
    if ref_section.doc_ctn_type.find("llamaparse") != -1:
        return False
    return True

def _find_ref_imgs_map(query: str, answer: str, ref_section: ScoredRecoveredSection) -> Tuple[dict, bool]:
    """
    优先从当前section找图，如果找不到且是低质量解析，
    那就往前后相邻的 chunk 搜索若干步看有没有图。
    """
    # 1. 先在当前 chunk 里扫描
    ref_img_fnames, ref_img_titles = _scan_markdown_for_ref_imgs(ref_section.content)
    if len(ref_img_fnames) > 0:
        return _construct_ref_imgs_map(ref_img_fnames, ref_img_titles, ref_section), False

    # 2. 若没有图片，并且是 llamaparse 之类的低质量解析，则尝试相邻 chunk
    if not _is_ctn_gen_by_high_quality_parse_engine(ref_section):
        return _find_ref_imgs_map_lqcut(query, answer, ref_section), True

    # 3. 若依然没有，返回空
    return {}, True

def _check_if_imgs_are_related_to_qa(user_query: str, llm_answer: str, knowledge_context: str, fname_and_titles: List[Tuple[str, str]]) -> List[Tuple[str, float]]:
    image_titles = [item[1] for item in fname_and_titles]
    rich.print(image_titles)

    numbered_image_descriptions = ""
    for ndx, image_title in enumerate(image_titles):
        numbered_image_descriptions += f"<image_description id='{ndx+1}'> {image_title.replace("\n", "")} </image_description>\n"
    numbered_image_descriptions += "\n"

    ref_img_fname_relevance_scores = []
    resp = check_img_relevance_by_gpt(user_query, llm_answer, knowledge_context, numbered_image_descriptions, model="gpt-4o-mini")
    rich.print(numbered_image_descriptions)
    logging.info(f"check_img_relevance_by_gpt: {resp}")
    rich.print(resp)

    image_relevance_scores = resp.get("image_relevance_scores", None)
    if image_relevance_scores is None:
        logging.error(f"not able to get right resp for img relevance: {resp}")
        return []

    sorted_id_to_scores = sorted(image_relevance_scores, key=lambda x: (x['relevance_score'], x['id']))
    for ndx, id_n_score in enumerate(sorted_id_to_scores):
        id = int(id_n_score["id"])
        id -= 1
        relevance_score = id_n_score["relevance_score"]
        if id >= 0 and id < len(fname_and_titles):
            fname = fname_and_titles[id][0]
            ref_img_fname_relevance_scores.append((fname, relevance_score))

    return ref_img_fname_relevance_scores

def _find_relavent_ref_imgs_map(query: str, answer: str, ref_section: ScoredRecoveredSection) -> dict:
    ref_img_map, _ = _find_ref_imgs_map(query, answer, ref_section)
    if len(ref_img_map) == 0:
        return {}

    fname_and_titles = []
    for ref_img_fname, pname_n_title in ref_img_map.items():
        fname_and_titles.append((ref_img_fname, pname_n_title[1]))

    ref_img_fname_relevance_scores = _check_if_imgs_are_related_to_qa(query, answer, ref_section.content, fname_and_titles)
    for fname_n_score in ref_img_fname_relevance_scores:
        fname, score = fname_n_score
        if score < MIN_IMG_RELEVANCE_SCORE:
            if fname in ref_img_map:
                del ref_img_map[fname]
    return ref_img_map


def search_for_file_refs(query: str, resp: dict, scored_sections_reranked:List[ScoredRecoveredSection], include_image: bool = True):
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
                if include_image:
                    refs_info[ref_doc_fname]["ref_imgs_map"] = _find_relavent_ref_imgs_map(query, answer, ref_section)

    rich.print(refs_info)
    return refs_info

if __name__ == "__main__":
    from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
    from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection
    from mrag_vdb.query.query2section_reranked import query2sortedsections_reranked
    from mrag_vdb.knowledge.query2knowledge import form_knowledge_snippets, gen_answer_from_knowledge_snippets

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

    knowledge_snippets = form_knowledge_snippets(scored_sections_reranked)

    resp = gen_answer_from_knowledge_snippets(query, knowledge_snippets)
    rich.print(resp)

    refs_info = search_for_file_refs(query, resp, scored_sections_reranked)
    print()
    rich.print(refs_info)
