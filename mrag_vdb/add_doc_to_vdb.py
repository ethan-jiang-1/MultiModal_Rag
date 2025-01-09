from typing import List
from dotenv import load_dotenv
import logging
import os

load_dotenv()


from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.build.doc2vdb import upsert_doc_to_vdb

def upsert_docs_to_vdb(pnames_final_info: List[str]) -> None:
    """
    Batch upsert multiple documents to vector database.
    
    Args:
        pnames_final_info: List of paths to document final info JSON files.
                         Each file contains metadata and content for a document.
    
    Note:
        - Processes each document sequentially
        - Logs progress and any errors
        - Skips files that don't exist
    """
    for ndx, pname_final_info in enumerate(pnames_final_info):
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

