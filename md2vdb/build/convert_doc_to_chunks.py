from dotenv import load_dotenv
import os
import sys
#import logging
import rich
import json
from typing import List, Tuple

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import PUBLIC_MIFN
from md2vdb.build.split_section_to_chunks import split_section_to_chunks
from md2vdb.common.doc_meta_info import DocMetaInfo
from md2vdb.common.chunked_section_info import ChunkedSectionInfo

def _get_collection_name(path_org_doc:str) -> str:
    dir_name = os.path.dirname(path_org_doc)
    collection_name = os.path.basename(dir_name)
    return collection_name

def _build_doc_meta_info(final_md_info: dict) -> DocMetaInfo:
    path_org_doc = final_md_info.get(PUBLIC_MIFN.PATHNAME_ORG_DOC)
    fname_org_doc = final_md_info.get(PUBLIC_MIFN.FNAME_ORG_DOC)
    fname_final_md = final_md_info.get(PUBLIC_MIFN.FNAME_FINAL_MD)
    doc_cnt_type = final_md_info.get(PUBLIC_MIFN.DOC_CTN_TYPE)
    doc_unique_id = final_md_info.get(PUBLIC_MIFN.DOC_UNIQUE_ID)
    doc_name_title = final_md_info.get(PUBLIC_MIFN.DOC_NAME_TITLE)
    doc_logic_title = final_md_info.get(PUBLIC_MIFN.DOC_LOGIC_TITLE)
    doc_summary = final_md_info.get(PUBLIC_MIFN.DOC_SUMMARY)
    collection_name = _get_collection_name(path_org_doc)     
    return DocMetaInfo(path_org_doc=path_org_doc,
                       fname_org_doc=fname_org_doc,
                       fname_final_md=fname_final_md,
                       doc_cnt_type=doc_cnt_type,
                       doc_unique_id=doc_unique_id,
                       doc_name_title=doc_name_title,
                       doc_logic_title=doc_logic_title,
                       doc_summary=doc_summary,
                       fnames_sec=final_md_info.get(PUBLIC_MIFN.FNAMES_SECS),
                       collection_name=collection_name)

def build_doc_meta_info(pname_final_md_info: str) -> DocMetaInfo:
    if not os.path.isfile(pname_final_md_info):
        raise ValueError(f"not found {pname_final_md_info}")
    
    with open(pname_final_md_info, encoding="utf-8") as f:
        final_md_info = json.load(f)

    doc_meta_info = _build_doc_meta_info(final_md_info)
    return doc_meta_info

def convert_sections_to_chunks(pname_final_md_info: str) -> Tuple[DocMetaInfo, List[ChunkedSectionInfo]]:
    doc_meta_info = build_doc_meta_info(pname_final_md_info)

    src_dir = os.path.dirname(pname_final_md_info)
    doc_unique_id = doc_meta_info.doc_unique_id
    doc_title = doc_meta_info.doc_logic_title
    all_csis = []
    for fname in doc_meta_info.fnames_sec:
        pname_md_section = os.path.join(src_dir, fname)
        if not os.path.isfile(pname_md_section):
            continue

        with open(pname_md_section, encoding="utf-8") as f:
            md_section = f.read()
        csis = split_section_to_chunks(md_section, doc_unique_id, doc_title=doc_title)
        all_csis.extend(csis)

    return doc_meta_info, all_csis

if __name__ == "__main__":
    pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"

    meta_info, all_csis = convert_sections_to_chunks(pname_final_md_info)
    rich.print(meta_info)
    rich.print(all_csis)

    path_meta_info = "_work/doc_meta_info.json"
    meta_info.save_to_file(path_meta_info)

    meta_info_new = DocMetaInfo.load_from_file(path_meta_info)
    rich.print(meta_info_new)
