import os 
import sys
from qdrant_client import QdrantClient


if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.doc_meta_info import DocMetaInfo

# Constants for paths and filenames
_VDB_PATH = "_ds_vdb"
_REF_PATH = "_ds_ref"
_FILENAME_DOC_META = "doc_meta.json"
_FILENAME_DOC2COL = "map_doc2col.json"


def get_vdb_path() -> str:
    """Get vector database path."""
    return _VDB_PATH


def get_ref_path() -> str:
    """Get reference data path."""
    return _REF_PATH


class QdrantClientContextManager:
    """
    Context manager for Qdrant client.
    Ensures proper client initialization and cleanup.
    """
    def __init__(self, *args, **kwargs):
        """Initialize Qdrant client with given arguments."""
        self.client = QdrantClient(*args, **kwargs)

    def __enter__(self) -> QdrantClient:
        """Enter context and return client."""
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close client on context exit."""
        self.client.close()


def get_ref_root(doc_meta_info: DocMetaInfo) -> str:
    """
    Get reference root directory for document.

    Args:
        doc_meta_info: Document metadata information

    Returns:
        str: Path to reference directory
    """
    collection_name = doc_meta_info.collection_name
    unique_name = doc_meta_info.doc_unique_id
    dir_ref = os.path.join(get_ref_path(), f"{collection_name}_{unique_name}")
    os.makedirs(dir_ref, exist_ok=True)
    return dir_ref


def get_doc_meta_pathname(doc_meta_info: DocMetaInfo) -> str:
    """
    Get document metadata file path.

    Args:
        doc_meta_info: Document metadata information

    Returns:
        str: Path to metadata file
    """
    dir_doc_meta = get_ref_root(doc_meta_info)
    pname_doc_meta = os.path.join(dir_doc_meta, _FILENAME_DOC_META)
    return pname_doc_meta


def get_map_doc2col_pathname() -> str:
    """
    Get document to collection mapping file path.

    Returns:
        str: Path to mapping file
    """
    path_map_doc2col = os.path.join(get_ref_path(), _FILENAME_DOC2COL)
    return path_map_doc2col


if __name__ == "__main__":
    # Test basic paths
    print(f"VDB Path: {get_vdb_path()}")
    print(f"Reference Path: {get_ref_path()}")
    print(f"Map Doc2Col Path: {get_map_doc2col_pathname()}")
