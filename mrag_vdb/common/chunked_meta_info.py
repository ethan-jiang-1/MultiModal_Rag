from dotenv import load_dotenv
import sys
from pydantic import BaseModel

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")



# this is going to be payload in vector db
class ChunkedSectionInfo(BaseModel):
    sec_id: str                 # section_number_in_str such as 1.2.4
    parent_sec_id: str          # parent section_number_in_str such as 1.2
    level: int                  # toc level
    order: int                  # order of chunk for the section, a section might be chunked into multiple chunks, 0-based.
    total: int                  # total of chunks that compose the section,  both order/total are two paramters that recover the full section
    heading: str                # heading/title of the secton
    desc: str                   # desc hiqa from top to current level
    max_tokens: int             # max_token_in_chunk
    doc_unique_id: str          # doc unique id
    doc_title: str              # doc title
    doc_ctn_type: str           # doc ctn type
    fname_org_doc: str          # doc file name
    content: str                # content (will be encoded to vector)
    sec_seq_no: int             # seq number at section level, 0-based

class ChunkedImageInfo(BaseModel):
    heading: str 
    desc: str
    doc_unique_id: str
    doc_title: str
    image_description: str 
    fname_image: str
    fname_org_doc: str
