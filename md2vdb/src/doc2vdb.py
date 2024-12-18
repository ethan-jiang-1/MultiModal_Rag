from dotenv import load_dotenv
#import os
import sys
import logging
import rich
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from dataclasses import fields

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.src.doc2chunks import convert_doc_to_chunks, DocMetaInfo
from md2vdb.src.section2chunks import ChunkedSectionInfo
from md2vdb.utils.utili_embedding import EMBEDDING_VEC_LEN, get_text_embedding
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.src.vdb_const import VDB_PATH

def _inject_chunks_into_vdb(client: QdrantClient, doc_meta_info: DocMetaInfo, all_csis: list[ChunkedSectionInfo], max_chunk_num=None):
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


def convert_doc_to_vdb(pname_final_md_info: str, max_chunk_num=None):
    doc_meta_info, all_csis = convert_doc_to_chunks(pname_final_md_info)
    if doc_meta_info is None:
        raise ValueError(f"not able to convert {pname_final_md_info}")
    
    vdb_path = VDB_PATH 
    client = QdrantClient(path=vdb_path)
    ret = _inject_chunks_into_vdb(client, doc_meta_info, all_csis, max_chunk_num=max_chunk_num)
    client.close()

    return ret


if __name__ == "__main__":
    setup_logger_handlers()

    pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"

    ret = convert_doc_to_vdb(pname_final_md_info)
    rich.print(ret)
