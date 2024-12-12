from dotenv import load_dotenv
#import os
import sys
#import logging
import rich
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import PUBLIC_MIFN

def convert_doc_to_chunks(chunked_md_info):
    meta_info = {}
    for key in [PUBLIC_MIFN.PATHNAME_ORG_DOC,
                PUBLIC_MIFN.FNAME_ORG_DOC,
                PUBLIC_MIFN.DOC_CTN_TYPE,
                PUBLIC_MIFN.DOC_UNIQUE_ID,
                PUBLIC_MIFN.DOC_NAME_TITLE,
                PUBLIC_MIFN.DOC_LOGIC_TITLE]:
        if key in chunked_md_info:
            meta_info[key] = chunked_md_info[key]

    return meta_info

if __name__ == "__main__":
    pname_chunked_md_info = "_work/ctn2md_深度学习在视电阻率快速反演中的研究_lvlm/_final.json"
    with open(pname_chunked_md_info, encoding="utf-8") as f:
        chunked_md_info = json.load(f)
    rich.print(chunked_md_info)

    meta_info = convert_doc_to_chunks(chunked_md_info)
    rich.print(meta_info)
