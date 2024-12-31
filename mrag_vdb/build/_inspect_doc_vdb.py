from typing import Dict
from dotenv import load_dotenv
import sys
import logging
import rich 


from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")


def cal_stats_for_doc_id(client: QdrantClient, 
                         collection_name: str, 
                         target_doc_unique_id: str, 
                         target_doc_title: str) -> Dict:
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

if __name__ == "__main__":
    from mrag_vdb.common.vdb_base import get_vdb_path, QdrantClientContextManager
    from mrag_vdb.common.doc_meta_info import DocMetaInfo
    import json

    #pname_doc_meta_info = "_ds_ref/mrag_5__back_panel_与环境匹配工程校核_P2_274ae6fb/doc_meta.json"
    pname_doc_meta_info = "_ds_ref/mrag_1__座椅STO间隙_P1_28b5d804/doc_meta.json"

    with open(pname_doc_meta_info, "r", encoding="utf-8") as f:
        data = json.load(f)
    doc_meta_info = DocMetaInfo(**data)
    rich.print(doc_meta_info)

    with QdrantClientContextManager(path=get_vdb_path()) as client:

        collection_name = doc_meta_info.collection_name
        target_doc_unique_id = doc_meta_info.doc_unique_id
        target_doc_title = doc_meta_info.doc_logic_title

        stats = cal_stats_for_doc_id(client, collection_name, target_doc_unique_id, target_doc_title)
        rich.print(stats)