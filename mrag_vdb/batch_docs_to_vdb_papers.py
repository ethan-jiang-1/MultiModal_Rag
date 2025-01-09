from dotenv import load_dotenv

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.batch_docs_to_vdb_mrag import upsert_batch_kbname_to_vdb 

KB_NAME = "papers"

if __name__ == "__main__":
    setup_logger_handlers()

    dir_root_mds = "_work"

    upsert_batch_kbname_to_vdb(dir_root_mds, kb_name=KB_NAME)

