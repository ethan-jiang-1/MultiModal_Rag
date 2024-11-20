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

def save_md_info(out_dir, md_info):
    if isinstance(md_info, dict):
        md_info["out_dir"] = out_dir
        md_info_path = os.path.join(out_dir, "info.json")
        json_str = json.dumps(md_info, indent=4, ensure_ascii=False)
        with open(md_info_path, 'w+', encoding='utf8') as f:
            f.write(json_str) 
        return md_info_path
    return None

def load_md_info(md_info_path):
    if os.path.isfile(md_info_path):
        with open(md_info_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    return None
