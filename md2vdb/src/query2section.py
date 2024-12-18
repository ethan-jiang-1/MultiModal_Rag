from dotenv import load_dotenv
import sys
import logging
import rich
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

from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.src.vdb_const import VDB_PATH
from md2vdb.utils.utili_embedding import get_text_embedding

LIMIT_QUERY = 5

logger = logging.getLogger(__name__)

@dataclass
class ScoredSection:
    """
    数据类表示完整的 Section。
    """
    sec_id: str
    parent_sec_id: str
    score: float
    content: str
    title: str
    desc: str
    doc_path: str
    doc_title: str
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


def _merge_chunks_to_sections(sections: Dict[str, Dict]) -> List[ScoredSection]:
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
        total = payload0.get("total", len(chunks))
        if total != len(chunks):
            logger.error(f"Not all chunks recovered for section {sec_id}")

        scored_section = ScoredSection(
            sec_id=sec_id,
            parent_sec_id=payload0.get("parent_sec_id"),
            score=max_score,
            content=content,
            title=payload0.get("title"),
            desc=payload0.get("desc"),
            doc_path=payload0.get("doc_path"),
            doc_title=payload0.get("doc_title"),
            payloads=[item[1].payload for item in chunks],
        )
        merged_scored_sections.append(scored_section)

        logger.info(f"Section {sec_id} restored with {len(chunks)} chunks and max score {max_score}.")
    return merged_scored_sections


def _get_initial_points(client: QdrantClient, query: str, collection_name: str, limit: int = LIMIT_QUERY) -> List[ScoredPoint]:
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


def query2section(collection_name: str, query: str, limit: int = LIMIT_QUERY) -> List[ScoredSection]:
    """
    查询集合中的 chunk 并恢复完整的 section。
    """
    if not VDB_PATH:
        logger.error("VDB_PATH is not set. Exiting...")
        return []

    client = QdrantClient(path=VDB_PATH)

    initial_points = _get_initial_points(client, query, collection_name, limit=limit)
    rich.print(initial_points)

    sections = _group_initial_chunks(initial_points)
    _query_missing_chunks(client, collection_name, sections)
    merged_sections = _merge_chunks_to_sections(sections)

    client.close()
    return merged_sections


if __name__ == "__main__":
    setup_logger_handlers()

    query = "神经网络"
    collection_name = "深度学习在视电阻率快速反演中的研究_6a2683b0"

    results = query2section(collection_name, query)
    rich.print(results)
