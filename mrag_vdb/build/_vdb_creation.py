#from pydantic import BaseModel
#from typing import Any, Dict, Union
from dotenv import load_dotenv
import sys
import rich
from qdrant_client import QdrantClient
import logging
from qdrant_client.http.models import VectorParams, Distance

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

#from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo
from mrag_vdb.common.text_embedding import _EMBEDDING_VEC_LEN
from mrag_vdb.utils.util_logging import setup_logger_handlers


def ensure_collection_with_schema_chunked_section(client: QdrantClient, collection_name: str) -> bool:
    # 检查集合是否存在
    if client.collection_exists(collection_name):
        return True 
    
    logging.info(f"create new vdb: {collection_name}")

    # 集合不存在，创建新的集合
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=_EMBEDDING_VEC_LEN, distance=Distance.COSINE)
    )
    logging.info(f"Collection '{collection_name}' created.")
    return True


if __name__ == "__main__":
    from mrag_vdb.common.vdb_base import VDB_PATH, QdrantClientContextManager
    setup_logger_handlers()

    with QdrantClientContextManager(path=VDB_PATH) as client:
        ensure_collection_with_schema_chunked_section(client, "testsp")
        collection = client.get_collection(collection_name="testsp")
        rich.print(collection)

    

