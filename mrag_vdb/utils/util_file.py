from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()

def get_root_dir() -> str:
    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  
    return root_dir