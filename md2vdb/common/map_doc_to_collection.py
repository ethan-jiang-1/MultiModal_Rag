from dotenv import load_dotenv
import sys
import os
from pydantic import BaseModel
from typing import List
import logging
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.common.doc_meta_info import DocMetaInfo
from md2vdb.common.chunked_section_info import ChunkedSectionInfo
from md2vdb.common.vdb_base import get_map_doc2col_pathname

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

def assign_collection_name_to_doc(doc_meta_info:DocMetaInfo, all_csis:List[ChunkedSectionInfo], collection_name_expected:str):
    path_map_doc2col = get_map_doc2col_pathname()
    md2c = MapDocToCol.load_from_file(path_map_doc2col)
    unique_id = doc_meta_info.doc_unique_id
    if collection_name_expected is None:
        if unique_id in md2c.map_doc2col:
            collection_name = md2c.map_doc2col[unique_id]
        else:
            collection_name = unique_id
    else:
        collection_name = collection_name_expected
    logging.info(f"collection_name: {collection_name}")
    md2c.map_doc2col[unique_id] = collection_name
    logging.info(f"map doc {unique_id} to  collection_name:{collection_name}")
    md2c.save_to_file(path_map_doc2col)
    return collection_name

if __name__ == "__main__":
    from md2vdb.build.convert_doc_to_chunks import convert_sections_to_chunks, DocMetaInfo

    pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    doc_meta_info, all_csis = convert_sections_to_chunks(pname_final_md_info)

    collection_name_expected = None
    collection_name = assign_collection_name_to_doc(doc_meta_info, all_csis, collection_name_expected)
    print(collection_name)

