from typing import List
from dotenv import load_dotenv
import os
import shutil
from llama_parse import LlamaParse


load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo

def safe_download_tables(parser:LlamaParse, json_result:List[dict], md_info:MdInfo):
    out_dir = md_info.get_out_dir()
    tables = parser.get_xlsx(json_result, out_dir)
    fnames_tbls = []
    for item in tables:
        fname_xlsx = os.path.basename(item["path"])
        fname_unique_xlsx = md_info.get_unique_job_id() + ".xlsx"
        if not os.path.isfile(fname_unique_xlsx):
            src_pathname = os.path.join(out_dir, fname_xlsx)
            dst_pathname = os.path.join(out_dir, fname_unique_xlsx)
            if dst_pathname != src_pathname:
                shutil.move(src_pathname, dst_pathname)
        fnames_tbls.append(fname_unique_xlsx)
    return fnames_tbls