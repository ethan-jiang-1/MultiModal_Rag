from dotenv import load_dotenv
import sys
import logging
import rich
import uuid
#import json

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, UpdateResult, Filter, FieldCondition

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.build.split_section_to_chunks import ChunkedSectionInfo
from mrag_vdb.utils.utili_embedding import EMBEDDING_VEC_LEN, get_text_embedding
from mrag_vdb.build.inspect_doc_vdb import cal_stats_for_doc_id


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
        stats = cal_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
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

    stats = cal_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
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
    stats = cal_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
    rich.print(f"[yellow]after inject_doc_chunks_into_vdb [/yellow]  {stats}")
    return ret

if __name__ == "__main__":
    from mrag_vdb.common.vdb_base import VDB_PATH, QdrantClientContextManager
    from mrag_vdb.build.build_doc_meta_info import build_doc_meta_info

    pname_final_info = "_work/ctn2md_mrag__5__back_panel_与环境匹配工程校核_P2_md/_final_info.json"
    doc_meta_info = build_doc_meta_info(pname_final_info)

    rich.print(doc_meta_info)

    with QdrantClientContextManager(path=VDB_PATH) as client:

        collection_name = doc_meta_info.collection_name
        target_doc_unique_id = doc_meta_info.doc_unique_id
        target_doc_title = doc_meta_info.doc_logic_title

        stats = cal_stats_for_doc_id(client, collection_name, target_doc_unique_id, target_doc_title)
        rich.print(stats)

