from dotenv import load_dotenv
#import os
import sys
#import logging
#import rich
#import random
#import re
#import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")
    
def get_job_id(unique_str):
    from ctn2md.utils.util_file import get_crc32_id
    return get_crc32_id(unique_str)
