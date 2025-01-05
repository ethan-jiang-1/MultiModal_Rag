from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class RagAnswer(BaseModel):
    """
    Model for RAG (Retrieval-Augmented Generation) answer results.
    Contains the answer and its associated source information.
    """
    answer: str = Field(
        description="Raw answer text from the model"
    )
    answer_referenced: str = Field(
        description="Answer with reference citations"
    )
    source_names: List[str] = Field(
        description="List of source document names",
        default_factory=list
    )
    source_titles: List[str] = Field(
        description="List of source document titles",
        default_factory=list
    )
    source_pnames: List[str] = Field(
        description="List of source document paths",
        default_factory=list
    )
    image_names: List[str] = Field(
        description="List of referenced image names",
        default_factory=list
    )
    image_titles: List[str] = Field(
        description="List of image titles",
        default_factory=list
    )
    image_pnames: List[str] = Field(
        description="List of image file paths",
        default_factory=list
    )

    class Config:
        """Pydantic model configuration"""
        validate_assignment = True
        extra = "forbid"


if __name__ == "__main__":
    # Create a sample RAG answer
    rag_answer = RagAnswer(
        answer="This is a sample answer.",
        answer_referenced="This is a sample answer [1].",
        source_names=["doc1"],
        source_titles=["Document 1"],
        source_pnames=["/path/to/doc1.pdf"],
        image_names=["img1"],
        image_titles=["Image 1"],
        image_pnames=["/path/to/img1.jpg"]
    )

    # Print the results
    print("RAG Answer Details:")
    print(f"Answer: {rag_answer.answer}")
    print(f"Referenced Answer: {rag_answer.answer_referenced}")
    print(f"Number of sources: {len(rag_answer.source_names)}")
    print(f"Number of images: {len(rag_answer.image_names)}")
    