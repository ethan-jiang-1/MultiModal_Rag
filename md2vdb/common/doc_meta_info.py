from dotenv import load_dotenv
import sys
import os
from pydantic import BaseModel
from typing import Optional, List
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

class DocSummary(BaseModel):
    """
    定义 DocSummary 模型
    """
    title: str
    summary: str
    keywords_top: str
    keywords_remain: str


class DocMetaInfo(BaseModel):
    """
    定义 DocMetaInfo 模型，嵌套 DocSummary
    """
    path_org_doc: str
    fname_org_doc: str
    fname_final_md: str
    doc_cnt_type: Optional[str]  # 可以是 str 或 None
    doc_unique_id: str
    doc_name_title: str
    doc_logic_title: str
    doc_summary: DocSummary  # 嵌套 DocSummary 模型
    fnames_sec: List[str]  # 字符串列表
    collection_name: str

    def save_to_file(self, path_meta_info):
        dir_name = os.path.dirname(path_meta_info)
        os.makedirs(dir_name, exist_ok=True)
        with open(path_meta_info, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))
        return True

    @classmethod
    def load_from_file(cls, path_meta_info):
        if not os.path.isfile(path_meta_info):
            return None
        with open(path_meta_info, "r", encoding="utf-8") as f:
            data = json.load(f)  # 从文件加载 JSON 数据
        meta_info_new = cls.model_validate(data) 
        return meta_info_new        


