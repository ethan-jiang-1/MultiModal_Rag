from dotenv import load_dotenv, find_dotenv
import os
import sys

if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

def get_root_dir():
    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  
    return root_dir