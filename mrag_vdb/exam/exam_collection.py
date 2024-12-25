from dotenv import load_dotenv
import sys
import rich

#from qdrant_client import QdrantClient
#from typing import List

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.vdb_base import VDB_PATH
from mrag_vdb.common.vdb_base import QdrantClientContextManager

def exam_collection(collection_name: str):
    """
    查询集合中的 chunk 并恢复完整的 section。
    """
    with QdrantClientContextManager(path=VDB_PATH) as client:
        collection = client.get_collection(collection_name=collection_name)
        rich.print(collection)


if __name__ == "__main__":
    setup_logger_handlers()
    exam_collection('mrag')

