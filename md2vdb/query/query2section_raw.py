from dotenv import load_dotenv
import sys
import rich

#from qdrant_client import QdrantClient
from typing import List

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.common.vdb_base import VDB_PATH
from md2vdb.query.query_bsae import ScoredSection
from md2vdb.query.recover_section_for_query import query_initial_points, recover_scored_sections_from_chunk_from_vdb, LIMIT_QUERY, sort_scored_sections_by_score
from md2vdb.utils.utili_embedding import get_text_embedding
from md2vdb.common.vdb_base import QdrantClientContextManager

def query2section_raw_on_single_collection(collection_name: str, query: str, limit: int = LIMIT_QUERY) -> List[ScoredSection]:
    """
    查询集合中的 chunk 并恢复完整的 section。
    """
    with QdrantClientContextManager(path=VDB_PATH) as client:
        query_vector = get_text_embedding(query)

        initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=limit)

        merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

    return merged_scored_sections


def query2section_raw_on_multiple_collection(collection_names: list[str], query: str, limit: int = LIMIT_QUERY) -> List[ScoredSection]:
    """
    查询集合中的 chunk 并恢复完整的 section。
    """
    with QdrantClientContextManager(path=VDB_PATH) as client:
        all_merged_scored_sections = []
        for collection_name in collection_names:
            query_vector = get_text_embedding(query)

            initial_scored_chunks = query_initial_points(client, collection_name, query_vector, limit=limit)

            merged_scored_sections = recover_scored_sections_from_chunk_from_vdb(client, collection_name, initial_scored_chunks)

            all_merged_scored_sections.extend(merged_scored_sections)
    
    all_merged_scored_sections = sort_scored_sections_by_score(all_merged_scored_sections)
    return all_merged_scored_sections

def test1():
    #query = "神经网络"
    query = "reference"
    collection_name = "papers"

    results = query2section_raw_on_single_collection(collection_name, query)
    rich.print(results)
    print()

    for ndx, result in enumerate(results):
        print()
        rich.print(f"[red]{(ndx, round(result.score, 4), result.sec_id, result.desc)}[/red]", "\n", result.content)

def test2():
    query = "fine-tuned chat models"

    collection_names = []
    collection_names.append("papers")
    collection_names.append("mrag")

    results = query2section_raw_on_multiple_collection(collection_names, query) 
    rich.print(results)
    print()

    for ndx, result in enumerate(results):
        print()
        rich.print(f"[red]{(ndx, round(result.score, 4), result.sec_id, result.desc)}[/red]", "\n", result.content)

def test3():
    query = "激励平台"

    collection_names = []
    collection_names.append("mrag")

    results = query2section_raw_on_multiple_collection(collection_names, query) 
    rich.print(results)
    print()

    for ndx, result in enumerate(results):
        print()
        rich.print(f"[red]{(ndx, round(result.score, 4), result.sec_id, result.desc)}[/red]", "\n", result.content)


if __name__ == "__main__":
    setup_logger_handlers()

    test1()
    #test2()
    #test3()



