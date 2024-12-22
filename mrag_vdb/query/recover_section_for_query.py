from dotenv import load_dotenv
import sys
import logging
#import rich
import re

from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint, Record, Filter, FieldCondition
from typing import List, Dict, Tuple, Union
from collections import defaultdict

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo
from mrag_vdb.common.vdb_base import QdrantClientContextManager
from mrag_vdb.query.query_bsae import ScoredSection

LIMIT_QUERY = 5

logger = logging.getLogger(__name__)


def _group_initial_chunks(initial_points: List[ScoredPoint]) -> Dict[str, Dict]:
    """
    按 sec_id 和 doc_unique_id 聚合初始 chunk 数据，以确保不同文件中的相同 sec_id 不会被错误合并。
    """
    sections = defaultdict(lambda: {"order_n_point": [], "max_score": 0.0, "metadata": None, "total": 0})

    for point in initial_points:
        sec_id = point.payload.get("sec_id")
        doc_unique_id = point.payload.get("doc_unique_id")  # 获取 doc_unique_id
        if sec_id is None or doc_unique_id is None:
            logger.warning("Missing sec_id or doc_unique_id in point payload, skipping point.")
            continue

        order = point.payload.get("order", 0)
        total = point.payload.get("total", 1)

        # 使用 (sec_id, doc_unique_id) 作为唯一的键
        section_key = (sec_id, doc_unique_id)

        sections[section_key]["order_n_point"].append((order, point))
        sections[section_key]["max_score"] = max(sections[section_key]["max_score"], getattr(point, "score", 0.0))
        sections[section_key]["metadata"] = point.payload
        sections[section_key]["total"] = total

    logger.info(f"Initial sections grouped by sec_id and doc_unique_id: {len(sections)} sections found.")
    return sections



def _query_missing_chunks(client: QdrantClient, collection_name: str, sections: Dict[str, Dict]) -> None:
    """
    查询缺失的 chunk 并补齐到 sections 字典中。
    """
    for sec_id, data in sections.items():
        existing_orders = {order for order, _ in data["order_n_point"]}
        total_chunks = data["total"]
        doc_unique_id = data["metadata"]["doc_unique_id"]
        missing_orders = [order for order in range(total_chunks) if order not in existing_orders]

        if missing_orders:
            logger.info(f"Section {sec_id} missing chunks: {missing_orders}")

            for missing_order in missing_orders:
                filter_query = Filter(
                    must=[
                        FieldCondition(key="sec_id", match={"value": sec_id}),
                        FieldCondition(key="order", match={"value": missing_order}),                        
                        FieldCondition(key="doc_unique_id", match={"value": doc_unique_id}),
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
                    data["order_n_point"].append((missing_order, point))
                else:
                    logger.warning(f"Chunk with sec_id={sec_id} and order={missing_order} not found.")

        # 排序数据，确保按照 order 升序排列
        data["order_n_point"].sort(key=lambda x: x[0])
    return sections

def _clean_chunk_content(content: str) -> str:
    """
    清理 chunk 内容，去除描述符 [desc] ... [desc] 及其包裹的内容。
    """
    cleaned_content = re.sub(r"\[desc\][^\[]*?\[desc\]\n?", "", content)
    return cleaned_content.strip()


def _clean_and_merge_chunks_content(chunks: List[Tuple[int, Union[ScoredPoint, Record]]]) -> str:
    """
    清理并合并所有 chunk 的内容。

    :param chunks: ScoredPoint 或 Point 列表，包含 order 和点信息。
    :return: 合并后的完整内容字符串。
    """
    chunks.sort(key=lambda x: x[0])  # 按 order 排序
    merged_content = ""
    for _, point in chunks:
        content = point.payload.get("content", "")
        if not content:
            logger.warning(f"Chunk {point.id} has empty or missing 'content'.")
            continue
        merged_content += _clean_chunk_content(content)
    return merged_content


def _merge_chunks_to_scored_sections(sections: Dict[str, Dict], collection_name:str) -> List[ScoredSection]:
    """
    合并所有 chunk，恢复完整的 section。
    """
    merged_scored_sections = []
    for section_key, data in sections.items():
        # 使用 (sec_id, doc_unique_id) 作为唯一的键
        # section_key = (sec_id, doc_unique_id)
        sec_id, _ = section_key

        chunks = data["order_n_point"]
        content = _clean_and_merge_chunks_content(chunks)

        # 计算最高分数
        max_score = max((getattr(point, "score", 0.0) for _, point in chunks), default=0.0)

        payload0 = chunks[0][1].payload
        csi0 = ChunkedSectionInfo(**payload0)
        if csi0.total != len(chunks):
            logger.error(f"Chunks recovered number misaligned for section {sec_id}: {csi0.total} != {len(chunks)}")

        payloads = []
        for _, chunk in chunks:
            payload = chunk.payload
            if isinstance(chunk, ScoredPoint):
                payload["score"] = chunk.score
            else:
                payload["score"] = 0.0
            payloads.append(payload)
        scored_section = ScoredSection(
            score=round(max_score, 5),
            sec_id=sec_id,
            parent_sec_id=csi0.parent_sec_id,
            level=csi0.level,
            heading=csi0.heading,
            desc=csi0.desc,
            doc_unique_id=csi0.doc_unique_id,
            doc_title=csi0.doc_title,
            doc_ctn_type=csi0.doc_ctn_type,
            fname_org_doc=csi0.fname_org_doc,
            content=content,
            sec_seq_no=csi0.sec_seq_no,
            payloads=payloads, 
            score_rrf=0.0,
            knowledge_snippet=None,
            collection_name=collection_name,
        )
        merged_scored_sections.append(scored_section)

        logger.info(f"Section {sec_id} restored with {len(chunks)} chunks and max score {max_score}.")
    return merged_scored_sections


def query_initial_points(client: QdrantClient, collection_name: str,  query_vector: List[float], limit: int = LIMIT_QUERY) -> List[ScoredPoint]:
    """
    获取初始 chunk 数据。
    """
    initial_points = client.search(
        collection_name=collection_name,
        query_vector=query_vector,                      
        limit=limit,
    )
    return initial_points

def recover_scored_sections_from_chunk_from_vdb(client: QdrantClient, collection_name: str, initial_scored_chunks: List[ScoredPoint]) -> List[ScoredSection]:
    sections = _group_initial_chunks(initial_scored_chunks)
    _query_missing_chunks(client, collection_name, sections)
    merged_scored_sections = _merge_chunks_to_scored_sections(sections, collection_name)
    return merged_scored_sections

def sort_scored_sections_by_score(sections: List[ScoredSection]) -> List[ScoredSection]:
    """
    对 ScoredSection 列表按照 score 降序排序。

    :param sections: ScoredSection 的列表
    :return: 按照 score 降序排序后的列表
    """
    return sorted(sections, key=lambda section: section.score, reverse=True)

if __name__ == "__main__":
    import rich
    from mrag_vdb.utils.utili_embedding import get_text_embedding
    from mrag_vdb.utils.util_logging import setup_logger_handlers
    from mrag_vdb.common.vdb_base import VDB_PATH

    setup_logger_handlers()

    query = "神经网络"
    collection_name = "papers"


    with QdrantClientContextManager(path=VDB_PATH) as client:
        query_vector = get_text_embedding(query)

        initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=5)

        merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

        rich.print(merged_scored_sections)
