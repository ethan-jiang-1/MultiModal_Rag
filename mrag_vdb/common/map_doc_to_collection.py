from dotenv import load_dotenv
import sys
import os
from pydantic import BaseModel
import logging
import json
import re

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.common.vdb_base import get_map_doc2col_pathname
from mrag_vdb.utils.util_logging import setup_logger_handlers

def decompose_doc_unique_id(doc_unique_id):
    pattern = r"^(.+?)_([a-f0-9]+)$"
    match = re.match(pattern, doc_unique_id)
    if match:
        doc_title = match.group(1)
        unique_id = match.group(2)
        return doc_title, unique_id
    else:
        return None, None

class MapDocToCol(BaseModel):
    map_doc2col: dict

    def save_to_file(self, path_map_doc2col):
        dir_name = os.path.dirname(path_map_doc2col)
        os.makedirs(dir_name, exist_ok=True)
        with open(path_map_doc2col, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))
        return True

    @classmethod
    def load_from_file(cls, path_map_doc2col):
        if not os.path.isfile(path_map_doc2col):
            return MapDocToCol(map_doc2col={})
        with open(path_map_doc2col, "r", encoding="utf-8") as f:
            data = json.load(f)  # 从文件加载 JSON 数据
        map_d2c = cls.model_validate(data) 
        return map_d2c

    @classmethod
    def validate_doc_title(cls, md2c, doc_unique_id):
        doc_title, unique_id = decompose_doc_unique_id(doc_unique_id)
        if doc_title is None:
            return False, f"invalid doc_unique_id: {doc_unique_id}"
        keys = md2c.map_doc2col.keys()
        for key in keys:
            if key.startswith(doc_title):
                if key != doc_unique_id:
                    return False, f"{doc_title} has defined in m2c already with {unique_id}"
        return True, None

    @classmethod
    def register_collection_name_for_doc(cls, doc_meta_info:DocMetaInfo):
        path_map_doc2col = get_map_doc2col_pathname()
        md2c = MapDocToCol.load_from_file(path_map_doc2col)
        doc_unique_id = doc_meta_info.doc_unique_id

        valid, err = cls.validate_doc_title(md2c, doc_unique_id)
        if not valid:
            return ValueError(err)

        changed = False
        if doc_unique_id in md2c.map_doc2col:
            collection_name = md2c.map_doc2col[doc_unique_id]
        else:
            collection_name = doc_meta_info.collection_name
            md2c.map_doc2col[doc_unique_id] = collection_name
            changed = True

        logging.info(f"collection_name: {collection_name}")
        if changed:
            logging.info(f"new map doc {doc_unique_id} to  collection_name:{collection_name}")
            md2c.save_to_file(path_map_doc2col)
        else:
            logging.info(f"existing map doc {doc_unique_id} to  collection_name:{collection_name}")
        return collection_name

if __name__ == "__main__":
    from mrag_vdb.build.convert_doc_to_chunks import build_doc_meta_info, DocMetaInfo

    setup_logger_handlers()

    pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    doc_meta_info = build_doc_meta_info(pname_final_md_info)

    collection_name_expected = None
    collection_name = MapDocToCol.register_collection_name_for_doc(doc_meta_info)
    print("regitered collection name: ", collection_name)

