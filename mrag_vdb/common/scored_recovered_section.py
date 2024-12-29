from dataclasses import dataclass
from typing import List, Any

@dataclass
class ScoredRecoveredSection:
    """
    Represents a recovered section with scores and metadata.
    Used to store section information retrieved from vector database.
    """
    # Scoring information
    score: float            # Embedding similarity score
    score_rrf: float       # Hybrid RRF (Reciprocal Rank Fusion) score

    # Section identification
    sec_id: str            # Section number in string format (e.g., "1.2.4")
    parent_sec_id: str     # Parent section number (e.g., "1.2")
    heading: str           # Section heading/title
    level: int            # TOC level (1-based)
    desc: str             # Hierarchical description from top to current level

    # Document information
    doc_unique_id: str     # Document unique identifier
    doc_title: str        # Document title
    doc_ctn_type: str     # Document content type
    fname_org_doc: str    # Original document filename
    content: str          # Section content
    sec_seq_no: int       # Sequential number at section level (0-based)

    # Additional metadata
    payloads: List[Any]   # Additional debugging information (merged chunks)
    knowledge_snippet: Any # Knowledge snippet for LLM content tracking
    collection_name: str   # Vector database collection name

