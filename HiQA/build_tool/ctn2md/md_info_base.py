from dotenv import load_dotenv
import os
import sys
#import logging
#import rich
#import random
import json

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

SEP_FNAME_EXT = "___"
FNAME_MD_INFO = "info.json"

def save_md_info(out_dir, md_info):
    if isinstance(md_info, dict):
        md_info_path = os.path.join(out_dir, FNAME_MD_INFO)
        json_str = json.dumps(md_info, indent=4, ensure_ascii=False)
        with open(md_info_path, 'w+', encoding='utf8') as f:
            f.write(json_str) 
        return md_info_path
    return None

def load_md_info(md_info_path):
    if os.path.isfile(md_info_path):
        try:
            with open(md_info_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except: # noqa 
            import json_repair
            with open(md_info_path, 'r', encoding='utf-8') as file:
                data = file.read()
            return json_repair.repair_json(data, return_objects=True, ensure_ascii=True)
    return None

def get_doc_type(md_info):
    if isinstance(md_info, dict):
        fname_org_doc = md_info.get("fname_org_doc", None)
        if fname_org_doc is not None:
            return fname_org_doc.split(".")[-1].lower()
    return ""

def find_md_info_path(filepath_in_out_dir):
    dir_name = os.path.dirname(filepath_in_out_dir)
    md_info_path = os.path.join(dir_name, FNAME_MD_INFO)
    if os.path.isfile(md_info_path):
        return md_info_path
    return None
