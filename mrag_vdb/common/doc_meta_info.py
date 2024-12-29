from typing import List, Optional
from dotenv import load_dotenv
import sys
import os
import json
from pydantic import BaseModel, Field

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

class DocSummary(BaseModel):
    """
    Document summary model containing key information about the document.
    """
    title: str = Field(
        description="Document title"
    )
    summary: str = Field(
        description="Document summary text"
    )
    keywords_top: str = Field(
        description="Top/primary keywords for the document"
    )
    keywords_remain: str = Field(
        description="Additional/secondary keywords"
    )


class DocMetaInfo(BaseModel):
    """
    Document metadata model containing comprehensive information about the document.
    """
    path_org_doc: str = Field(
        description="Path to the original document"
    )
    fname_org_doc: str = Field(
        description="Original document filename"
    )
    fname_final_md: str = Field(
        description="Final markdown filename"
    )
    doc_cnt_type: str = Field(
        description="Document content type"
    )
    doc_unique_id: str = Field(
        description="Unique identifier for the document"
    )
    doc_name_title: str = Field(
        description="Document name/title"
    )
    doc_logic_title: str = Field(
        description="Logical title for the document"
    )
    doc_summary: DocSummary = Field(
        description="Document summary information"
    )
    fnames_sec: List[str] = Field(
        description="List of section filenames",
        default_factory=list
    )
    collection_name: str = Field(
        description="Name of the document collection"
    )

    def save_to_file(self, path_meta_info: str) -> bool:
        """
        Save metadata to a JSON file.

        Args:
            path_meta_info: Path where to save the metadata

        Returns:
            bool: True if save was successful
        """
        dir_name = os.path.dirname(path_meta_info)
        os.makedirs(dir_name, exist_ok=True)
        with open(path_meta_info, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))
        return True

    @classmethod
    def load_from_file(cls, path_meta_info: str) -> Optional['DocMetaInfo']:
        """
        Load metadata from a JSON file.

        Args:
            path_meta_info: Path to the metadata file

        Returns:
            Optional[DocMetaInfo]: Loaded metadata object or None if file doesn't exist
        """
        if not os.path.isfile(path_meta_info):
            return None
        with open(path_meta_info, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)


if __name__ == "__main__":
    # Create a sample document summary
    doc_summary = DocSummary(
        title="Sample Document",
        summary="This is a sample document summary.",
        keywords_top="key1, key2, key3",
        keywords_remain="key4, key5, key6"
    )

    # Create a sample document metadata
    doc_meta = DocMetaInfo(
        path_org_doc="/path/to/original.pdf",
        fname_org_doc="original.pdf",
        fname_final_md="final.md",
        doc_cnt_type="PDF",
        doc_unique_id="doc123",
        doc_name_title="Sample Document",
        doc_logic_title="Sample Document - Technical Report",
        doc_summary=doc_summary,
        fnames_sec=["section1.md", "section2.md"],
        collection_name="technical_docs"
    )

    # Save to file
    meta_file = "_test/doc_meta_info_sample.json"
    doc_meta.save_to_file(meta_file)
    print(f"Saved metadata to {meta_file}")

    # Load and verify
    loaded_meta = DocMetaInfo.load_from_file(meta_file)
    if loaded_meta:
        print("\nLoaded metadata:")
        print(f"Title: {loaded_meta.doc_name_title}")
        print(f"Summary: {loaded_meta.doc_summary.summary}")
        print(f"Keywords: {loaded_meta.doc_summary.keywords_top}")


