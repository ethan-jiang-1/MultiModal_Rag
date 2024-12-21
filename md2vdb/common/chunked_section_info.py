from dotenv import load_dotenv
import sys
from pydantic import BaseModel

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")



# this is going to be payload in vector db
class ChunkedSectionInfo(BaseModel):
    sec_id: str
    parent_sec_id: str
    level: int
    order: int
    total: int
    heading: str
    desc: str
    max_tokens_in_chunk: int
    doc_unique_id: str 
    doc_title: str
    fname_org_doc: str
    content: str