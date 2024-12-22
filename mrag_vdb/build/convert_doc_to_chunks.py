from dotenv import load_dotenv
import os
import sys
#import logging
import rich
#import json
from typing import List, Tuple

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.build.split_section_to_chunks import split_section_to_chunks
from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.common.chunked_meta_info import ChunkedSectionInfo
from mrag_vdb.build.build_doc_meta_info import build_doc_meta_info


def convert_sections_to_chunks(pname_final_md_info: str) -> Tuple[DocMetaInfo, List[ChunkedSectionInfo]]:
    doc_meta_info = build_doc_meta_info(pname_final_md_info)

    src_dir = os.path.dirname(pname_final_md_info)
    doc_unique_id = doc_meta_info.doc_unique_id
    doc_title = doc_meta_info.doc_logic_title
    fname_org_doc = doc_meta_info.fname_org_doc
    all_csis = []
    for fname in doc_meta_info.fnames_sec:
        pname_md_section = os.path.join(src_dir, fname)
        if not os.path.isfile(pname_md_section):
            continue

        with open(pname_md_section, encoding="utf-8") as f:
            md_section = f.read()
        csis = split_section_to_chunks(md_section, doc_unique_id, doc_title=doc_title, fname_org_doc=fname_org_doc)
        all_csis.extend(csis)

    return doc_meta_info, all_csis

if __name__ == "__main__":
    pname_final_md_info = "_work/ctn2md_mrag__1__座椅STO间隙_P1_lp/_final_info.json"

    meta_info, all_csis = convert_sections_to_chunks(pname_final_md_info)
    rich.print(meta_info)
    rich.print(all_csis)

    path_meta_info = "_work/doc_meta_info.json"
    meta_info.save_to_file(path_meta_info)

    meta_info_new = DocMetaInfo.load_from_file(path_meta_info)
    rich.print(meta_info_new)
