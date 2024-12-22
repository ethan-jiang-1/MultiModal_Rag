from typing import List
from dotenv import load_dotenv
import sys
import logging
import os
#import rich


load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

_MIB_CTN2MD_LEAD = "ctn2md"

from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.build.doc2vdb import upsert_doc_to_vdb

def upsert_docs_to_vdb(pnames_final_info: List[str]):
    for ndx, pname_final_info in enumerate(pnames_final_info):
        logging.info(f"{ndx} updata doc to vdb: {pname_final_info}")
        if os.path.isfile(pname_final_info):
            upsert_doc_to_vdb(pname_final_info)
        else:
            logging.error(f"failed to find {pname_final_info}")

def upsert_batch_kbname_to_vdb(dir_root_mds, kb_name=None):
    if kb_name is None:
        raise ValueError("kb_name(collection_name) need to be specified")
    if not os.path.isdir(dir_root_mds):
        raise ValueError(f"{dir_root_mds} is not a dir")
    
    names = os.listdir(dir_root_mds)
    sel_names = []
    names = sorted(names)
    for name in names:
        if not name.startswith(f"{_MIB_CTN2MD_LEAD}_{kb_name}__"):
            continue
        sel_name = os.path.join(dir_root_mds, name, "_final_info.json")
        if os.path.isfile(sel_name):
            sel_names.append(sel_name)

    logging.info(f"find total {len(sel_names)} for {kb_name}")
    for ndx, pname_final_info in enumerate(sel_names):
        logging.info(f"{ndx} updata doc to vdb: {pname_final_info}")
        if os.path.isfile(pname_final_info):
            upsert_doc_to_vdb(pname_final_info)
        else:
            logging.error(f"failed to find {pname_final_info}")

if __name__ == "__main__":
    setup_logger_handlers()

    pnames_final_info = ["_work/ctn2md_papers__深度学习在视电阻率快速反演中的研究_lvlm/_final_info.json", 
                         "_work/ctn2md_papers__Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json",
                         "_work/ctn2md_papers__attention_is_all_you_need_lvlm/_final_info.json",
                         "_work/ctn2md_papers__Winning_Solution_For_Meta_KDD_Cup__24_2410_00005v1_lvlm/_final_info.json"]

    upsert_docs_to_vdb(pnames_final_info)

