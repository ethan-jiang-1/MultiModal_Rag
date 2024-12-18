from dotenv import load_dotenv
import os
import sys
#import logging
import rich
import shutil

from qdrant_client import QdrantClient

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.build.convert_doc_to_chunks import convert_sections_to_chunks, DocMetaInfo
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.common.vdb_base import VDB_PATH, get_doc_meta_pathname, get_ref_root
from md2vdb.build.inject_chunks_to_vdb import inject_doc_chunks_into_vdb
from md2vdb.common.map_doc_to_collection import assign_collection_name_for_doc

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


def upsert_doc_to_vdb(pname_final_md_info: str, max_chunk_num:int = None, skip_build_vdb:bool = False):
    doc_meta_info, all_csis = convert_sections_to_chunks(pname_final_md_info)
    if doc_meta_info is None:
        raise ValueError(f"not able to convert {pname_final_md_info}")
    
    collection_name = assign_collection_name_for_doc(doc_meta_info)
    
    if not skip_build_vdb:
        vdb_path = VDB_PATH 
        client = QdrantClient(path=vdb_path)
        inject_doc_chunks_into_vdb(client, collection_name, doc_meta_info, all_csis, max_chunk_num=max_chunk_num)
        client.close()

    _save_doc_meta_info(doc_meta_info)

    _copy_all_ref_files(doc_meta_info, pname_final_md_info)

    return collection_name


if __name__ == "__main__":
    setup_logger_handlers()

    pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"
    #pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    skip_build_vdb = False
    #skip_build_vdb = True

    collection_name = None
    max_chunk_num = None

    ret = upsert_doc_to_vdb(pname_final_md_info, max_chunk_num=max_chunk_num, skip_build_vdb=skip_build_vdb)
    rich.print(ret)
