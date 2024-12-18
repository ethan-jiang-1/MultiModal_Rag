from dotenv import load_dotenv
import sys
import rich

from qdrant_client import QdrantClient
from typing import List

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.common.vdb_base import VDB_PATH
from md2vdb.query.recover_section_for_query import query_initial_points, recover_section_from_vdb, ScoredSection, LIMIT_QUERY


def query2section_on_single_collection(collection_name: str, query: str, limit: int = LIMIT_QUERY) -> List[ScoredSection]:
    """
    查询集合中的 chunk 并恢复完整的 section。
    """
    client = QdrantClient(path=VDB_PATH)

    initial_points = query_initial_points(client, collection_name, query, limit=limit)

    merged_scored_sections = recover_section_from_vdb(client, collection_name, initial_points)

    client.close()
    return merged_scored_sections


if __name__ == "__main__":
    setup_logger_handlers()

    query = "神经网络"
    collection_name = "深度学习在视电阻率快速反演中的研究_6a2683b0"
    #collection_name = "Survey_of_different_Large_Language_Model_Architectures_bd72132b"

    results = query2section_on_single_collection(collection_name, query)
    rich.print(results)
