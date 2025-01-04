from typing import Optional
from dotenv import load_dotenv
import os
import logging
import rich
import shutil

load_dotenv()

from mrag_vdb.build._convert_doc_to_chunks import convert_sections_to_chunks, DocMetaInfo
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.vdb_base import get_vdb_path, get_doc_meta_pathname, get_ref_root
from mrag_vdb.build._inject_chunks_to_vdb import inject_doc_chunks_into_vdb
from mrag_vdb.common.map_doc_to_collection import MapDocToCol
from mrag_vdb.common.vdb_base import QdrantClientContextManager

def _save_doc_meta_info(doc_meta_info:DocMetaInfo) -> None:
    pname_meta_doc = get_doc_meta_pathname(doc_meta_info)
    with open(pname_meta_doc, "w", encoding="utf-8") as f:
        f.write(doc_meta_info.model_dump_json(indent=4))


def _copy_all_ref_files(doc_meta_info:DocMetaInfo, pname_final_info: str) -> None:
    dir_src = os.path.dirname(pname_final_info)
    dir_dst = get_ref_root(doc_meta_info)

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


def upsert_doc_to_vdb(pname_final_info: str, max_chunk_num:Optional[int] = None, skip_build_vdb:bool = False) -> str:
    if not pname_final_info.endswith("_final_info.json"):
        raise ValueError("only take _final_info.json as input")

    doc_meta_info, all_csis = convert_sections_to_chunks(pname_final_info)
    if doc_meta_info is None:
        raise ValueError(f"not able to convert {pname_final_info}")
    
    collection_name = MapDocToCol.register_collection_name_for_doc(doc_meta_info)
    logging.info(f"upsert_doc_to_vdb: {collection_name} <- {pname_final_info}")
    
    if not skip_build_vdb:
        with QdrantClientContextManager(path=get_vdb_path()) as client:
            inject_doc_chunks_into_vdb(client, collection_name, doc_meta_info, all_csis, max_chunk_num=max_chunk_num)

    _save_doc_meta_info(doc_meta_info)

    _copy_all_ref_files(doc_meta_info, pname_final_info)

    return collection_name


if __name__ == "__main__":
    setup_logger_handlers()

    #pname_final_info = "_work/ctn2md_mrag__1__座椅STO间隙_P1_lp/_final_info.json"
    #pname_final_info = "_work/ctn2md_mrag__5__back_panel_与环境匹配工程校核_P2_md/_final_info.json"
    #pname_final_info = "_work/ctn2md_papers____AI+应用_百花齐放_新质生产力前景广阔pdf_lvlm/_final_info.json"
    pname_final_info = "_work/ctn2md_mrag__1__座椅STO间隙_P1_lp/_final_info.json"

    skip_build_vdb = False
    #skip_build_vdb = True

    collection_name = None
    max_chunk_num = None

    ret = upsert_doc_to_vdb(pname_final_info, max_chunk_num=max_chunk_num, skip_build_vdb=skip_build_vdb)
    rich.print(ret)
