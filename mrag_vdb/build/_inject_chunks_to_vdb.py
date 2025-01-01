from typing import Dict, Optional
from dotenv import load_dotenv
import sys
import logging
import rich
import uuid
#import json

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, UpdateResult, Filter, FieldCondition

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.build._split_section_to_chunks import ChunkedSectionInfo
from mrag_vdb.common.text_embedding import get_embedding_vec
from mrag_vdb.build._inspect_doc_vdb import cal_stats_for_doc_id
from mrag_vdb.common.map_doc_to_collection import MapDocToCol
from mrag_vdb.build._vdb_with_extra_info import ensure_collection_refreshed


def _prepare_collection_for_reinject_doc(client: QdrantClient, collection_name: str, doc_meta_info: DocMetaInfo) -> Dict:
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
    ensure_collection_refreshed(client, collection_name, doc_meta_info)
    logging.info(f"update existing vdb: {collection_name}")

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
    
    collection = client.get_collection(collection_name=collection_name)
    rich.print(collection_name, collection)

    return stats

def _update_doc_to_collection(client: QdrantClient, 
                              stats0: dict, 
                              stats1: dict, 
                              collection_name: str, 
                              doc_meta_info: DocMetaInfo, 
                              all_cisi: list[ChunkedSectionInfo]) -> None:
    collection = client.get_collection(collection_name=collection_name)
    item_add = stats1["total_items"] - stats0["total_items"]
    MapDocToCol.update_collection_name_for_doc(doc_meta_info, collection_name, collection, item_add)

def inject_doc_chunks_into_vdb(client: QdrantClient, 
                               collection_name:str, 
                               doc_meta_info: DocMetaInfo, 
                               all_csis: list[ChunkedSectionInfo], 
                               max_chunk_num:Optional[int] = None) -> UpdateResult:
    stats0 = _prepare_collection_for_reinject_doc(client, collection_name, doc_meta_info)

    total = len(all_csis)
    sec_seq_no = -1
    cur_sec_id = "no"
    batch_size = 8  # 每批处理8个点
    final_ret = None

    # 准备所有的向量和payload
    vectors = []
    payloads = []
    for ndx, csi in enumerate(all_csis):
        logging.info(f"converting doc_chunk {ndx+1}/{total} for {collection_name}")
        vector = get_embedding_vec(csi.content)
        if csi.sec_id != cur_sec_id:
            cur_sec_id = csi.sec_id
            sec_seq_no += 1
        csi.sec_seq_no = sec_seq_no
        payload = csi.model_dump()
        vectors.append(vector)
        payloads.append(payload)
        if max_chunk_num is not None and ndx + 1 == max_chunk_num:
            break

    # 分批处理
    for i in range(0, len(vectors), batch_size):
        batch_vectors = vectors[i:i + batch_size]
        batch_payloads = payloads[i:i + batch_size]
        
        batch_points = [
            PointStruct(id=str(uuid.uuid4()), vector=batch_vectors[j], payload=batch_payloads[j])
            for j in range(len(batch_vectors))
        ]
        logging.info(f"upserting batch {i//batch_size + 1}, size: {len(batch_points)}")

        ret = client.upsert(
            collection_name=collection_name,
            points=batch_points,
        )
        final_ret = ret  # 保存最后一次的返回结果
        rich.print(ret)

    doc_unique_id = doc_meta_info.doc_unique_id
    doc_title = doc_meta_info.doc_logic_title
    stats1 = cal_stats_for_doc_id(client, collection_name, doc_unique_id, doc_title)
    rich.print(f"[yellow]after inject_doc_chunks_into_vdb [/yellow]  {stats1}")

    _update_doc_to_collection(client, stats0, stats1, collection_name, doc_meta_info, all_csis)
    return final_ret

if __name__ == "__main__":
    from mrag_vdb.common.vdb_base import get_vdb_path, QdrantClientContextManager
    from mrag_vdb.build.build_doc_meta_info import build_doc_meta_info

    pname_final_info = "_work/ctn2md_mrag__5__back_panel_与环境匹配工程校核_P2_md/_final_info.json"
    doc_meta_info = build_doc_meta_info(pname_final_info)

    rich.print(doc_meta_info)

    with QdrantClientContextManager(path=get_vdb_path()) as client:

        collection_name = doc_meta_info.collection_name
        target_doc_unique_id = doc_meta_info.doc_unique_id
        target_doc_title = doc_meta_info.doc_logic_title

        stats = cal_stats_for_doc_id(client, collection_name, target_doc_unique_id, target_doc_title)
        rich.print(stats)

