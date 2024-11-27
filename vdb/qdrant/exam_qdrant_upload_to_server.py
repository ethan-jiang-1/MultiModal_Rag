import sys
#import json
import rich
#import os
from dotenv import load_dotenv  # , find_dotenv
#import logging
from qdrant_client import QdrantClient

load_dotenv()
if './' not in sys.path:
    sys.path.append('./')

from text2sql.util.util_logging import setup_logger_handlers
from data_source.util.util_vectordb import VDB_DISTANCE, VDB_VECTOR_SIZE
setup_logger_handlers()

def _get_all_local_points(local_client, collection_name):
    # Retrieve all points from the collection using `scroll`
    local_points = []
    scroll = local_client.scroll(
        collection_name=collection_name,
        with_payload=True,  # Include payloads
        with_vectors=True   # Include vectors
    )

    while scroll:
        batch, next_scroll_id = scroll
        local_points.extend(batch)
        if next_scroll_id:
            scroll = local_client.scroll(
                collection_name=collection_name,
                scroll_filter=None,
                offset=next_scroll_id,
                with_payload=True,
                with_vectors=True
            )
        else:
            break
    return local_points

def _upload_snapshot_to_server(rag_path, collection_name):
    local_client = QdrantClient(path=rag_path)

    local_points = _get_all_local_points(local_client, collection_name)

    for ndx, point in enumerate(local_points):
        rich.print(ndx, point.payload)

    # 连接到服务器版 Qdrant 实例 (make sure your localhost qdrant docker is running)
    server_client = QdrantClient(url="http://localhost:6333")

    # 创建 collection
    ret1 = server_client.recreate_collection(
        collection_name=collection_name,
        vectors_config={"size": VDB_VECTOR_SIZE, "distance": VDB_DISTANCE}  # 替换为你的向量维度和距离度量
    )
    rich.print(ret1)

    server_points = [
    {
        "id": record.id,
        "vector": record.vector,
        "payload": record.payload
    }
    for record in local_points  # Replace with your list of Record objects
    ]

    # 导入数据
    ret2 = server_client.upsert(
        collection_name=collection_name,
        points=server_points
    )
    rich.print(ret2)    

if __name__ == "__main__":
    setup_logger_handlers()

    from data_source.util.util_query_expert_zeroshot import RAG_PATH_EXPERT_ZEROSHOT, COLLECTION_NAME_EXPERT_ZEROSHOT
    rag_path = RAG_PATH_EXPERT_ZEROSHOT
    collection_name = COLLECTION_NAME_EXPERT_ZEROSHOT

    _upload_snapshot_to_server(rag_path, collection_name)
