import logging
import os
from dotenv import load_dotenv

load_dotenv()


from mrag_vdb.build.doc2vdb import upsert_doc_to_vdb
from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.add_doc_to_vdb import _MIB_CTN2MD_LEAD 

KB_NAME = "mrag"

def upsert_batch_kbname_to_vdb(dir_root_mds: str, kb_name: str = None) -> None:
    """
    Upsert all documents from a knowledge base directory to vector database.
    
    Args:
        dir_root_mds: Root directory containing markdown documents
        kb_name: Knowledge base name (collection name in vector database)
    
    Raises:
        ValueError: If kb_name is not specified or dir_root_mds is not a directory
    
    Note:
        - Processes all documents with matching kb_name prefix
        - Documents must follow naming pattern: ctn2md_{kb_name}__*
        - Each document directory must contain _final_info.json
        - Processes documents in sorted order
    """
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

    dir_root_mds = "_work"

    upsert_batch_kbname_to_vdb(dir_root_mds, kb_name=KB_NAME)

