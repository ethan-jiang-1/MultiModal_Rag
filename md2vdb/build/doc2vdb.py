from dotenv import load_dotenv
import os
import sys
import logging
import rich
import uuid
import shutil

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, UpdateResult
from dataclasses import fields

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.build.doc2chunks import convert_doc_to_chunks, DocMetaInfo
from md2vdb.build.section2chunks import ChunkedSectionInfo
from md2vdb.utils.utili_embedding import EMBEDDING_VEC_LEN, get_text_embedding
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.common.vdb_const import VDB_PATH, get_doc_meta_pathname, get_ref_root

def _inject_chunks_into_vdb(client: QdrantClient, doc_meta_info: DocMetaInfo, all_csis: list[ChunkedSectionInfo], max_chunk_num=None) -> UpdateResult:
    collection_name = doc_meta_info.doc_unique_id
    
    # 创建集合
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=EMBEDDING_VEC_LEN, distance=Distance.COSINE),
    )

    vectors = []
    payloads = []
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

    ret = client.upsert(
        collection_name=collection_name,
        points=points,
    )
    return ret

def _save_doc_meta_info(doc_meta_info:DocMetaInfo):
    collection_name = doc_meta_info.doc_unique_id
    pname_meta_doc = get_doc_meta_pathname(collection_name)
    with open(pname_meta_doc, "w", encoding="utf-8") as f:
        f.write(doc_meta_info.model_dump_json(indent=4))


def _copy_all_ref_files(doc_meta_info:DocMetaInfo, pname_final_md_info: str):
    dir_src = os.path.dirname(pname_final_md_info)
    collection_name = doc_meta_info.doc_unique_id
    dir_dst = get_ref_root(collection_name)

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


def convert_doc_to_vdb(pname_final_md_info: str, max_chunk_num:int = None, skip_build_vdb:bool = False):
    doc_meta_info, all_csis = convert_doc_to_chunks(pname_final_md_info)
    if doc_meta_info is None:
        raise ValueError(f"not able to convert {pname_final_md_info}")
    
    ret = None
    if not skip_build_vdb:
        vdb_path = VDB_PATH 
        client = QdrantClient(path=vdb_path)
        ret = _inject_chunks_into_vdb(client, doc_meta_info, all_csis, max_chunk_num=max_chunk_num)
        client.close()

    _save_doc_meta_info(doc_meta_info)

    _copy_all_ref_files(doc_meta_info, pname_final_md_info)

    return ret


if __name__ == "__main__":
    setup_logger_handlers()

    #pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"
    pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    #skip_build_vdb = False
    skip_build_vdb = True

    ret = convert_doc_to_vdb(pname_final_md_info, skip_build_vdb=skip_build_vdb)
    rich.print(ret)
