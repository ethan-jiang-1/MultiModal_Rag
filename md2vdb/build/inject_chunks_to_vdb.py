from dotenv import load_dotenv
import sys
import logging
import rich
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, UpdateResult, Filter, FieldCondition

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.common.doc_meta_info import DocMetaInfo
from md2vdb.build.split_section_to_chunks import ChunkedSectionInfo
from md2vdb.utils.utili_embedding import EMBEDDING_VEC_LEN, get_text_embedding


def _collection_stats_for_doc_id(client: QdrantClient, collection_name: str, target_doc_unique_id: str, target_doc_title: str):
    """
    统计集合中的点信息：
    1. 总项数
    2. payload 中 `doc_unique_id` 完全匹配的项数
    3. payload 中 `doc_title` 完全匹配的项数
    
    :param client: Qdrant 客户端实例
    :param collection_name: 集合名称
    :param target_doc_unique_id: 用于查询的 doc_unique_id
    :param target_doc_title: 用于查询的 doc_title
    :return: 包含统计信息的字典
    """
    stats = {"total_items": 0, "unique_id_match": 0, "title_match": 0}

    # 1. 获取集合总项数
    try:
        collection_info = client.get_collection(collection_name)
        stats["total_items"] = collection_info.points_count
    except Exception as e:
        logging.error(f"Error fetching collection stats: {e}")

    # 2. 查询完全匹配的 doc_unique_id
    try:
        unique_id_match_filter = Filter(
            must=[
                FieldCondition(key="doc_unique_id", match={"value": target_doc_unique_id})
            ]
        )
        unique_id_match_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=unique_id_match_filter,
            limit=1000,  # 最大滚动限制
            with_vectors=False
        )
        stats["unique_id_match"] = len(unique_id_match_result[0])
    except Exception as e:
        logging.error(f"Error fetching collection stats: {e}")

    # 3. 查询前缀匹配的 doc_title
    try:
        title_matchfilter = Filter(
            must=[
                FieldCondition(key="doc_title", match={"value": target_doc_title})
            ]
        )
        title_match_result = client.scroll(
            collection_name=collection_name,
            scroll_filter=title_matchfilter,
            limit=1000,  # 最大滚动限制
            with_vectors=False
        )
        stats["title_match"] = len(title_match_result[0])
    except Exception as e:
        logging.error(f"Error fetching collection stats: {e}")
        
    return stats


def _prepare_collection_for_reinject_doc(client: QdrantClient, collection_name: str, doc_meta_info: DocMetaInfo):
    """
    准备 Qdrant 集合：
    1. 如果集合不存在，则创建集合。
    2. 如果集合存在，清理与指定 doc_unique_id 匹配的点的 payload。
    
    :param client: Qdrant 客户端实例
    :param collection_name: 集合名称
    :param doc_meta_info: 包含文档元信息的 DocMetaInfo 实例
    """
    doc_unique_id = doc_meta_info.doc_unique_id
    doc_title = doc_meta_info.doc_logic_title

    # 检查集合是否存在
    if not client.collection_exists(collection_name):
        # 集合不存在，创建新的集合
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_VEC_LEN, distance=Distance.COSINE),
        )
        logging.info(f"Collection '{collection_name}' created.")
    else:
        stats = _collection_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
        rich.print(f"[yellow]before cleanup[/yellow] {stats}")
        # 集合存在，清理与 doc_unique_id 匹配的点
        filter_query = Filter(
            must=[
                FieldCondition(key="doc_unique_id", match={"value": doc_unique_id})
            ]
        )
        # 删除匹配点
        deleted_points = client.delete(
            collection_name=collection_name,
            points_selector=filter_query
        )
        logging.info(f"Deleted {deleted_points} points from collection '{collection_name}' with doc_unique_id='{doc_unique_id}'.")

    stats = _collection_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
    rich.print(f"[yellow]after cleanup[/yellow] {stats}")
    logging.info(f"collection '{collection_name}' with doc_unique_id='{doc_unique_id} stats: {stats}")

def inject_doc_chunks_into_vdb(client: QdrantClient, collection_name:str, doc_meta_info: DocMetaInfo, all_csis: list[ChunkedSectionInfo], max_chunk_num=None) -> UpdateResult:
    vectors = []
    payloads = []

    _prepare_collection_for_reinject_doc(client, collection_name, doc_meta_info)

    total = len(all_csis)
    for ndx, csi in enumerate(all_csis):
        logging.info(f"converting doc_chunk {ndx+1}/{total} for {collection_name}")
        vector = get_text_embedding(csi.content)
        payload = csi.model_dump()
        vectors.append(vector)
        payloads.append(payload)
        if max_chunk_num is None:
            if ndx + 1 == max_chunk_num:
                break

    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload=payloads[i])  # 使用 UUID 作为 ID
        for i in range(len(vectors))
    ]
    logging.info(f"total {len(points)} points need to be upsert")

    ret = client.upsert(
        collection_name=collection_name,
        points=points,
    )
    rich.print(ret)

    doc_unique_id = doc_meta_info.doc_unique_id
    doc_title = doc_meta_info.doc_logic_title
    stats = _collection_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
    rich.print(f"[yellow]after inject_doc_chunks_into_vdb [/yellow]  {stats}")
    return ret

if __name__ == "__main__":
    pass