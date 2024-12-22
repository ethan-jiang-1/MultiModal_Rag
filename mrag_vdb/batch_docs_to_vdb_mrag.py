from dotenv import load_dotenv
import sys


load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.add_doc_to_vdb import upsert_batch_kbname_to_vdb 

KB_NAME = "mrag"

if __name__ == "__main__":
    setup_logger_handlers()

    dir_root_mds = "_work"

    upsert_batch_kbname_to_vdb(dir_root_mds, kb_name=KB_NAME)

