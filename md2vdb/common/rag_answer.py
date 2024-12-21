from dotenv import load_dotenv
import sys
from pydantic import BaseModel
from typing import List


load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

class RagAnswer(BaseModel):
    answer: str
    answer_referenced: str 
    sources: List[str]
    image_names: List[str] 
    image_titles: List[str]
    