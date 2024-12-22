from dotenv import load_dotenv
import os
import sys
import rich
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import PUBLIC_MIFN
from md2vdb.common.doc_meta_info import DocMetaInfo



# Have to track back to original doc, as we are going to use folder name of the org doc as collection_name
def _get_org_doc_and_collection_name(final_md_info):
    pname_org_doc = final_md_info.get(PUBLIC_MIFN.PATHNAME_ORG_DOC)
    if pname_org_doc.endswith(".md"):
        src_doc = final_md_info.get(PUBLIC_MIFN.PATHNAME_SRC_DOC, None)
        if src_doc is not None:
            pname_org_doc = src_doc
    dir_name = os.path.dirname(pname_org_doc)
    collection_name = os.path.basename(dir_name)
    return pname_org_doc, collection_name

def _build_doc_meta_info_core(final_md_info: dict) -> DocMetaInfo:
    #fname_org_doc = final_md_info.get(PUBLIC_MIFN.FNAME_ORG_DOC)
    fname_final_md = final_md_info.get(PUBLIC_MIFN.FNAME_FINAL_MD)
    doc_cnt_type = final_md_info.get(PUBLIC_MIFN.DOC_CTN_TYPE)
    doc_unique_id = final_md_info.get(PUBLIC_MIFN.DOC_UNIQUE_ID)
    doc_name_title = final_md_info.get(PUBLIC_MIFN.DOC_NAME_TITLE)
    doc_logic_title = final_md_info.get(PUBLIC_MIFN.DOC_LOGIC_TITLE)
    doc_summary = final_md_info.get(PUBLIC_MIFN.DOC_SUMMARY)

    path_org_doc, collection_name = _get_org_doc_and_collection_name(final_md_info)
    fname_org_doc = os.path.basename(path_org_doc)

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

    doc_meta_info = _build_doc_meta_info_core(final_md_info)
    return doc_meta_info


if __name__ == "__main__":
    pname_final_md_info = "_work/ctn2md_mrag__1__座椅STO间隙_P1_lp/_final_info.json"
    doc_meta_info = build_doc_meta_info(pname_final_md_info)
    rich.print(doc_meta_info)    