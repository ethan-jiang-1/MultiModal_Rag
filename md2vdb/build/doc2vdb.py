from dotenv import load_dotenv
import os
import sys
import logging
import rich
import uuid
import shutil

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, UpdateResult, Filter, FieldCondition
from dataclasses import fields

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.build.doc2chunks import convert_doc_to_chunks, DocMetaInfo
from md2vdb.build.section2chunks import ChunkedSectionInfo
from md2vdb.utils.utili_embedding import EMBEDDING_VEC_LEN, get_text_embedding
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.common.vdb_const import VDB_PATH, get_doc_meta_pathname, get_ref_root


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
        rich.print("[yellow]before cleanup[/yellow]", stats)
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
    rich.print("[yellow]after cleanup[/yellow]", stats)
    logging.info(f"collection '{collection_name}' with doc_unique_id='{doc_unique_id} stats: {stats}")

def _inject_doc_chunks_into_vdb(client: QdrantClient, collection_name:str, doc_meta_info: DocMetaInfo, all_csis: list[ChunkedSectionInfo], max_chunk_num=None) -> UpdateResult:
    vectors = []
    payloads = []

    _prepare_collection_for_reinject_doc(client, collection_name, doc_meta_info)

    total = len(all_csis)
    for ndx, csi in enumerate(all_csis):
        logging.info(f"converting doc_chunk {ndx+1}/{total} for {collection_name}")
        vector = get_text_embedding(csi.content)
        payload = {}
        for field in fields(csi):
            payload[field.name] = getattr(csi, field.name)
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
    return ret

def _save_doc_meta_info(doc_meta_info:DocMetaInfo):
    pname_meta_doc = get_doc_meta_pathname(doc_meta_info.doc_unique_id)
    with open(pname_meta_doc, "w", encoding="utf-8") as f:
        f.write(doc_meta_info.model_dump_json(indent=4))


def _copy_all_ref_files(doc_meta_info:DocMetaInfo, pname_final_md_info: str):
    dir_src = os.path.dirname(pname_final_md_info)
    dir_dst = get_ref_root(doc_meta_info.doc_unique_id)

    # copy all images refered by md
    names = os.listdir(dir_src)
    for name in names:
        pathname = os.path.join(dir_src, name)
        if not os.path.isfile(pathname):
            continue 
        copy = False
        for ext in [".jpg", ".png"]:
            if name.endswith(ext):
                copy = True
                break 
        if copy:
            src_path = os.path.join(dir_src, name)
            dst_path = os.path.join(dir_dst, name)
            shutil.copy(src_path, dst_path)
    
    # copy the final md
    src_path = os.path.join(dir_src, doc_meta_info.fname_org_doc)
    dst_path = os.path.join(dir_dst, doc_meta_info.fname_org_doc)
    if os.path.isfile(src_path):
        shutil.copy(src_path, dst_path)

    # copy the final md
    src_path = os.path.join(dir_src, doc_meta_info.fname_final_md)
    dst_path = os.path.join(dir_dst, doc_meta_info.fname_final_md)
    if os.path.isfile(src_path):
        shutil.copy(src_path, dst_path)    

    # copy the original doc
    src_path = doc_meta_info.path_org_doc
    dst_path = os.path.join(dir_dst, os.path.basename(src_path))
    if os.path.isfile(src_path):
        shutil.copy(src_path, dst_path)


def convert_doc_to_vdb(pname_final_md_info: str,  collection_name:str, max_chunk_num:int = None, skip_build_vdb:bool = False):
    doc_meta_info, all_csis = convert_doc_to_chunks(pname_final_md_info)
    if doc_meta_info is None:
        raise ValueError(f"not able to convert {pname_final_md_info}")
    
    if collection_name is None:
        collection_name = doc_meta_info.doc_unique_id
    logging.info(f"collection_name: {collection_name}")
    
    if not skip_build_vdb:
        vdb_path = VDB_PATH 
        client = QdrantClient(path=vdb_path)
        _inject_doc_chunks_into_vdb(client, collection_name, doc_meta_info, all_csis, max_chunk_num=max_chunk_num)
        client.close()

    _save_doc_meta_info(doc_meta_info)

    _copy_all_ref_files(doc_meta_info, pname_final_md_info)

    return collection_name


if __name__ == "__main__":
    setup_logger_handlers()

    #pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"
    pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    skip_build_vdb = False
    #skip_build_vdb = True

    collection_name = None
    max_chunk_num = None

    ret = convert_doc_to_vdb(pname_final_md_info, collection_name, max_chunk_num=max_chunk_num, skip_build_vdb=skip_build_vdb)
    rich.print(ret)
