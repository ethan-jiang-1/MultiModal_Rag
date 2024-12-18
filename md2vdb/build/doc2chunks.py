from dotenv import load_dotenv
import os
import sys
#import logging
import rich
import json
#from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import PUBLIC_MIFN
from md2vdb.build.section2chunks import chunk_section_to_chunks

class DocSummary(BaseModel):
    """
    定义 DocSummary 模型
    """
    title: str
    summary: str
    keywords_top: str
    keywords_remain: str


class DocMetaInfo(BaseModel):
    """
    定义 DocMetaInfo 模型，嵌套 DocSummary
    """
    path_org_doc: str
    fname_org_doc: str
    doc_cnt_type: Optional[str]  # 可以是 str 或 None
    doc_unique_id: str
    doc_name_title: str
    doc_logic_title: str
    doc_summary: DocSummary  # 嵌套 DocSummary 模型
    fnames_sec: List[str]  # 字符串列表


def _build_doc_meta_info(final_md_info):
    path_org_doc = final_md_info.get(PUBLIC_MIFN.PATHNAME_ORG_DOC)
    fname_org_doc = final_md_info.get(PUBLIC_MIFN.FNAME_ORG_DOC)
    doc_cnt_type = final_md_info.get(PUBLIC_MIFN.DOC_CTN_TYPE)
    doc_unique_id = final_md_info.get(PUBLIC_MIFN.DOC_UNIQUE_ID)
    doc_name_title = final_md_info.get(PUBLIC_MIFN.DOC_NAME_TITLE)
    doc_logic_title = final_md_info.get(PUBLIC_MIFN.DOC_LOGIC_TITLE)
    doc_summary = final_md_info.get(PUBLIC_MIFN.DOC_SUMMARY)     
    return DocMetaInfo(path_org_doc=path_org_doc,
                       fname_org_doc=fname_org_doc,
                       doc_cnt_type=doc_cnt_type,
                       doc_unique_id=doc_unique_id,
                       doc_name_title=doc_name_title,
                       doc_logic_title=doc_logic_title,
                       doc_summary=doc_summary,
                       fnames_sec=final_md_info.get(PUBLIC_MIFN.FNAMES_SECS))

def convert_doc_to_chunks(pname_final_md_info):
    if not os.path.isfile(pname_final_md_info):
        raise ValueError(f"not found {pname_final_md_info}")
    
    with open(pname_final_md_info, encoding="utf-8") as f:
        final_md_info = json.load(f)

    doc_meta_info = _build_doc_meta_info(final_md_info)

    src_dir = os.path.dirname(pname_final_md_info)
    doc_path = doc_meta_info.path_org_doc
    doc_title = doc_meta_info.doc_logic_title
    all_csis = []
    for fname in doc_meta_info.fnames_sec:
        pname_md_section = os.path.join(src_dir, fname)
        if not os.path.isfile(pname_md_section):
            continue

        with open(pname_md_section, encoding="utf-8") as f:
            md_section = f.read()
        csis = chunk_section_to_chunks(md_section, doc_path=doc_path, doc_title=doc_title)
        all_csis.extend(csis)

    return doc_meta_info, all_csis

if __name__ == "__main__":
    pname_final_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json"

    meta_info, all_csis = convert_doc_to_chunks(pname_final_md_info)
    rich.print(meta_info)
    rich.print(all_csis)

    path_meta_info = "_work/doc_meta_info.json"
    with open(path_meta_info, "w", encoding="utf-8") as f:
        f.write(meta_info.model_dump_json(indent=4))

    with open(path_meta_info, "r", encoding="utf-8") as f:
        data = json.load(f)  # 从文件加载 JSON 数据
    meta_info_new = DocMetaInfo.model_validate(data) 
    rich.print(meta_info_new)
