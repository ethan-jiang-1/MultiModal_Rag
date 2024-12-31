import os
import sys 

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MdInfo

def generate_markdown_textin(md_info:MdInfo):
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    raise ValueError("not implemented yet")