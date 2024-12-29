from dotenv import load_dotenv
import sys
import json
from pydantic import BaseModel, Field

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

class ChunkedSectionInfo(BaseModel):
    """
    Metadata model for document section chunks.
    Used as payload in vector database to store section metadata.
    """
    sec_id: str = Field(
        description="Section number in string format, e.g., '1.2.4'"
    )
    parent_sec_id: str = Field(
        description="Parent section number in string format, e.g., '1.2'"
    )
    level: int = Field(
        description="TOC level, 1-based"
    )
    order: int = Field(
        description="Order of chunk within the section, 0-based",
        ge=0
    )
    total: int = Field(
        description="Total number of chunks in the section",
        gt=0
    )
    heading: str = Field(
        description="Section heading/title"
    )
    desc: str = Field(
        description="Hierarchical description from top to current level"
    )
    max_tokens: int = Field(
        description="Maximum number of tokens in chunk",
        gt=0
    )
    doc_unique_id: str = Field(
        description="Unique identifier of the document"
    )
    doc_title: str = Field(
        description="Document title"
    )
    doc_ctn_type: str = Field(
        description="Document content type"
    )
    fname_org_doc: str = Field(
        description="Original document filename"
    )
    content: str = Field(
        description="Content to be encoded as vector"
    )
    sec_seq_no: int = Field(
        description="Sequential number at section level, 0-based",
        ge=0
    )

    class Config:
        """Pydantic model configuration"""
        validate_assignment = True
        extra = "forbid"


if __name__ == "__main__":
    import rich
    # Create a sample instance
    sample_chunk = ChunkedSectionInfo(
        sec_id="1.2.3",
        parent_sec_id="1.2",
        level=3,
        order=0,
        total=5,
        heading="Sample Section",
        desc="Chapter 1 > Section 2 > Subsection 3",
        max_tokens=512,
        doc_unique_id="doc123",
        doc_title="Sample Document",
        doc_ctn_type="PDF",
        fname_org_doc="sample.pdf",
        content="This is a sample content section.",
        sec_seq_no=2
    )

    # Save to JSON file
    json_file = "_test/chunked_meta_info_sample.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_chunk.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Saved model to {json_file}")

    # Load from JSON file
    with open(json_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    loaded_chunk = ChunkedSectionInfo(**loaded_data)
   
    rich.print(loaded_chunk)
