import os 

VDB_PATH = "_ds_vdb"
REF_PATH = "_ds_ref"

FILENAME_DOC_META = "doc_meta.json"

def get_ref_root(unique_name: str) -> str:
    dir_ref = os.path.join(REF_PATH, unique_name)
    os.makedirs(dir_ref, exist_ok=True)
    return dir_ref

def get_doc_meta_pathname(unique_name: str) -> str:
    dir_collection = get_ref_root(unique_name)
    pname_doc_meta = os.path.join(dir_collection, FILENAME_DOC_META)
    return pname_doc_meta


if __name__ == "__main__":
    unique_name = "深度学习在视电阻率快速反演中的研究_6a2683b0"
    pname = get_doc_meta_pathname(unique_name)
    print(pname)

    ref_root = get_ref_root(unique_name)
    print(pname)
