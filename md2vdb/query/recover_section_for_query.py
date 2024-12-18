from dotenv import load_dotenv
import sys
import logging
#import rich
import re

from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint, Record, Filter, FieldCondition
from typing import List, Dict, Tuple, Union, Any
from collections import defaultdict
from dataclasses import dataclass

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.common.chunked_section_info import ChunkedSectionInfo
from md2vdb.utils.utili_embedding import get_text_embedding

LIMIT_QUERY = 5

logger = logging.getLogger(__name__)

@dataclass
class ScoredSection:
    """
    数据类表示完整的 Section。
    """
    score: float
    sec_id: str
    parent_sec_id: str
    heading: str
    level: int
    desc: str
    doc_unique_id: str
    doc_title: str
    content: str
    payloads: list[Any]


def _group_initial_chunks(initial_points: List[ScoredPoint]) -> Dict[str, Dict]:
    """
    按 sec_id 聚合初始 chunk 数据。
    """
    sections = defaultdict(lambda: {"chunks": [], "max_score": 0.0, "metadata": None, "total": 0})

    for point in initial_points:
        sec_id = point.payload.get("sec_id")
        if sec_id is None:
            logger.warning("Missing sec_id in point payload, skipping point.")
            continue

        order = point.payload.get("order", 0)
        total = point.payload.get("total", 1)

        sections[sec_id]["chunks"].append((order, point))
        sections[sec_id]["max_score"] = max(sections[sec_id]["max_score"], getattr(point, "score", 0.0))
        sections[sec_id]["metadata"] = point.payload
        sections[sec_id]["total"] = total

    logger.info(f"Initial sections grouped by sec_id: {len(sections)} sections found.")
    return sections


def _query_missing_chunks(client: QdrantClient, collection_name: str, sections: Dict[str, Dict]) -> None:
    """
    查询缺失的 chunk 并补齐到 sections 字典中。
    """
    for sec_id, data in sections.items():
        existing_orders = {order for order, _ in data["chunks"]}
        total_chunks = data["total"]
        missing_orders = [order for order in range(total_chunks) if order not in existing_orders]

        if missing_orders:
            logger.info(f"Section {sec_id} missing chunks: {missing_orders}")

            for missing_order in missing_orders:
                filter_query = Filter(
                    must=[
                        FieldCondition(key="sec_id", match={"value": sec_id}),
                        FieldCondition(key="order", match={"value": missing_order}),
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
                    data["chunks"].append((missing_order, point))
                else:
                    logger.warning(f"Chunk with sec_id={sec_id} and order={missing_order} not found.")


def _clean_chunk_content(content: str) -> str:
    """
    清理 chunk 内容，去除描述符 [desc] ... [desc] 及其包裹的内容。
    """
    #cleaned_content = re.sub(r"\[desc\].*?\[desc\]\n?", "", content, flags=re.DOTALL)
    #cleaned_content = re.sub(r"\[desc\][\s\S]*?\[desc\]", "", content)
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


def _merge_chunks_to_scored_sections(sections: Dict[str, Dict]) -> List[ScoredSection]:
    """
    合并所有 chunk，恢复完整的 section。
    """
    merged_scored_sections = []
    for sec_id, data in sections.items():
        chunks = data["chunks"]
        content = _clean_and_merge_chunks_content(chunks)

        # 计算最高分数
        max_score = max((getattr(point, "score", 0.0) for _, point in chunks), default=0.0)

        payload0 = chunks[0][1].payload
        csi0 = ChunkedSectionInfo(**payload0)
        if csi0.total != len(chunks):
            logger.error(f"Not all chunks recovered for section {sec_id}")

        payloads = []
        for _, chunk in chunks:
            payload = chunk.payload
            if isinstance(chunk, ScoredPoint):
                payload["score"] = chunk.score
            else:
                payload["score"] = 0.0
            payloads.append(payload)
        scored_section = ScoredSection(
            score=max_score,
            sec_id=sec_id,
            parent_sec_id=csi0.parent_sec_id,
            level=csi0.level,
            heading=csi0.heading,
            desc=csi0.desc,
            doc_unique_id=csi0.doc_unique_id,
            doc_title=csi0.doc_title,
            content=content,
            payloads=payloads
        )
        merged_scored_sections.append(scored_section)

        logger.info(f"Section {sec_id} restored with {len(chunks)} chunks and max score {max_score}.")
    return merged_scored_sections


def query_initial_points(client: QdrantClient, collection_name: str,  query: str, limit: int = LIMIT_QUERY) -> List[ScoredPoint]:
    """
    获取初始 chunk 数据。
    """
    query_vector = get_text_embedding(query)

    initial_points = client.search(
        collection_name=collection_name,
        query_vector=query_vector,                      
        limit=limit,
    )
    return initial_points

def recover_section_from_vdb(client: QdrantClient, collection_name: str, initial_points: List[ScoredPoint]) -> List[ScoredSection]:
    sections = _group_initial_chunks(initial_points)
    _query_missing_chunks(client, collection_name, sections)
    merged_scored_sections = _merge_chunks_to_scored_sections(sections)
    return merged_scored_sections


if __name__ == "__main__":
    pass