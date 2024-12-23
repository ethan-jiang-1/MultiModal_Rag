from dataclasses import dataclass
from typing import List, Any

# Original section recovered from vector db from chunks
# most content are from ChunkedSectionInfo
# but add some additional info: scores and knowledge_snippet etc. 
@dataclass
class ScoredRecoveredSection:
    """
    数据类表示完整的 Section。
    """
    score: float            # score - embedding
    score_rrf: float        # score - hybrid RRF

    sec_id: str             # section_number_in_str such as 1.2.4
    parent_sec_id: str      # parent section_number_in_str such as 1.2
    heading: str            # heading/title of the secton
    level: int              # toc level
    desc: str               # heading/title of the secton
    doc_unique_id: str      # doc unique id
    doc_title: str          # doc title
    doc_ctn_type: str       # doc ctn type
    fname_org_doc: str      # doc file name
    content: str            # content (will be encoded to vector)
    sec_seq_no: int         # seq number at section level, 0-based

    payloads: List[Any]     # additional info: for debugging (all chunks merged)
    knowledge_snippet: Any  # additional info: knowledge snippet -- for tracking llm content
    collection_name:str     # addintional info: collection_name
