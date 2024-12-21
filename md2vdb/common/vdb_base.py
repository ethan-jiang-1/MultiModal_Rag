import os 
import sys
if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.common.doc_meta_info import DocMetaInfo

VDB_PATH = "_ds_vdb"
REF_PATH = "_ds_ref"

FILENAME_DOC_META = "doc_meta.json"
FILENAME_COLLECTION = "collection_map.json"
FILENAME_DOC2COL = "map_doc2col.json"

def get_ref_root(doc_meta_info: DocMetaInfo) -> str:
    collection_name = doc_meta_info.collection_name
    unique_name = doc_meta_info.doc_unique_id
    dir_ref = os.path.join(REF_PATH, f"{collection_name}_{unique_name}")
    os.makedirs(dir_ref, exist_ok=True)
    return dir_ref

def get_doc_meta_pathname(doc_meta_info: DocMetaInfo) -> str:
    dir_doc_meta = get_ref_root(doc_meta_info)
    pname_doc_meta = os.path.join(dir_doc_meta, FILENAME_DOC_META)
    return pname_doc_meta

def get_map_doc2col_pathname() -> str:
    path_map_doc2col = os.path.join(REF_PATH, FILENAME_DOC2COL)
    return path_map_doc2col

if __name__ == "__main__":
    pname = get_map_doc2col_pathname()
    print(pname)
