from dotenv import load_dotenv
import rich
from qdrant_client import QdrantClient
import logging
from qdrant_client.http.models import VectorParams, Distance
from qdrant_client.local.qdrant_local import QdrantLocal

load_dotenv()

from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.common.text_embedding import get_embeding_len
from mmbase.utils.util_logging import setup_logger_handlers

def ensure_collection_refreshed(client: QdrantClient, collection_name: str, doc_meta_info: DocMetaInfo) -> bool:
    # 检查集合是否存在
    if not client.collection_exists(collection_name):
        logging.info(f"create new vdb: {collection_name}")

        # 集合不存在，创建新的集合
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=get_embeding_len(), distance=Distance.COSINE)
        )
        logging.info(f"Collection '{collection_name}' created.")
    else:
        collection = client.get_collection(collection_name=collection_name)
        is_empty_collection = (collection.points_count == 0)

        vector_size = collection.config.params.vectors.size
        if vector_size != get_embeding_len():
            if isinstance(client._client, QdrantLocal):
                del collection
                if not is_empty_collection:
                    raise ValueError(f"Collection '{collection_name}' has different vector size: {vector_size} vs {get_embeding_len()}. and it is not empty")
                client.delete_collection(collection_name=collection_name)

                # 集合存在，需要刷新， 可能embedding长度发生变化
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=get_embeding_len(), distance=Distance.COSINE)
                )
                logging.info(f"Collection '{collection_name}' refreshed at local.")
            else:
                error = f"Collection '{collection_name}' has different vector size: {vector_size} vs {get_embeding_len()}."
                logging.error(error)
                raise ValueError(error)

    return True


if __name__ == "__main__":
    from mrag_vdb.common.vdb_base import get_vdb_path, QdrantClientContextManager
    setup_logger_handlers()

    with QdrantClientContextManager(path=get_vdb_path()) as client:
        ensure_collection_refreshed(client, "testsp")
        collection = client.get_collection(collection_name="testsp")
        rich.print(collection)

    

