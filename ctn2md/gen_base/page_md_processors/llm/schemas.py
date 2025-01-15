"""
Data Models for LLM Analysis Results

Core Design Principles:
1. Completeness First: Ensure no potential headings are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class TableRange(BaseModel):
    """Table Range - Precisely locate table positions"""
    start: int
    end: int
    header: bool = False

class MergeAction(BaseModel):
    """Merge Action - Handle cross-page content"""
    type: str = "table"
    pages: List[int]
    line_ranges: Dict[str, List[dict]]
    confidence: float

class RemoveAction(BaseModel):
    """Remove Action - Handle redundant content"""
    page: int
    lines: List[int]
    reason: str
    confidence: float

class Warning(BaseModel):
    """Warning Information - Record uncertain judgments"""
    type: str
    page: int
    lines: List[int]
    message: str

class PageDebugInfo(BaseModel):
    """Page Debug Info - Record detailed page statistics"""
    page: int
    total_lines: int
    heading_count: int = Field(description="Number of headings in this page")
    table_count: int = Field(description="Number of tables in this page")
    image_count: int = Field(description="Number of images in this page")
    first_line_preview: str = Field(description="First 32 characters of the first line")
    last_line_preview: str = Field(description="First 32 characters of the last line")

class DocumentDebugInfo(BaseModel):
    """Document Debug Info - Record overall document statistics"""
    total_pages: int
    pages: List[PageDebugInfo]

class DocumentAnalysis(BaseModel):
    """Document Analysis Result - Integrate all analysis information"""
    debug_info: DocumentDebugInfo
    remove_actions: Optional[List[RemoveAction]] = []
    merge_actions: Optional[List[MergeAction]] = []
    warnings: Optional[List[Warning]] = []

if __name__ == "__main__":
    # Create a test document analysis result
    test_doc = {
        "debug_info": {
            "total_pages": 3,
            "pages": [
                {
                    "page": 1,
                    "total_lines": 25,
                    "heading_count": 2,
                    "table_count": 1,
                    "image_count": 0,
                    "first_line_preview": "[P1-L1] # 深度学习在视电阻率快速反演中",
                    "last_line_preview": "[P1-L25] **Abstract** In the field"
                }
            ]
        }
    }
    
    # Validate the document
    result = DocumentAnalysis.model_validate(test_doc)
    print("Valid document analysis:", result)
    
    # Test with invalid document
    invalid_doc = {
        "debug_info": {
            "total_pages": 1,
            "pages": ["invalid page info"]  # This should cause validation error
        }
    }
    try:
        DocumentAnalysis.model_validate(invalid_doc)
    except Exception as e:
        print("Expected validation error:", e) 