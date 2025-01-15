"""
Data Models for LLM Analysis Results

Core Design Principles:
1. Completeness First: Ensure no potential headings are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

from typing import List, Dict, Optional
import os
import rich 
from enum import Enum
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Base Enums
class ContentType(str, Enum):
    """Content type enumeration"""
    TABLE = "table"      # Table content

class RemoveReason(str, Enum):
    """Removal reason enumeration"""
    DUPLICATE = "duplicate"  # Duplicate content
    NOISE = "noise"         # Noise content
    INVALID = "invalid"     # Invalid content
    FOOTER = "footer"       # Page footer
    HEADER = "header"       # Page header

class WarningType(str, Enum):
    """Warning type enumeration"""
    OVERLAP = "overlap"      # Content overlap
    INCOMPLETE = "incomplete" # Incomplete content
    AMBIGUOUS = "ambiguous"  # Ambiguous content
    STRUCTURE = "structure"  # Structure issue
    FORMAT = "format"       # Format issue

# Base Data Classes
class LineRange(BaseModel):
    """Line range - Locates content position within a page
    
    Attributes:
        start: Starting line number (1-based), must be greater than 0
        end: Ending line number (1-based), must be greater than or equal to start
        is_header: Whether this is a header section (table-specific)
        has_separator: Whether it contains separator line (table-specific)
    """
    start: int = Field(gt=0, description="Starting line number (1-based)")
    end: int = Field(..., description="Ending line number (1-based)")
    is_header: bool = Field(default=False, description="Whether this is a header section")
    has_separator: bool = Field(default=False, description="Whether it contains separator line (---)")

    @property
    def validate_end(self) -> None:
        """Validate that end is greater than or equal to start"""
        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start")

class HeadingInfo(BaseModel):
    """Heading information - Describes document heading structure
    
    Attributes:
        page: Page number, must be greater than 0
        line: Line number, must be greater than 0
        level: Heading level (1-6)
        content: Heading content, must not be empty
        confidence: Confidence score (0.0-1.0)
    """
    page: int = Field(gt=0, description="Page number")
    line: int = Field(gt=0, description="Line number")
    level: int = Field(ge=1, le=6, description="Heading level (1-6)")
    content: str = Field(min_length=1, description="Heading content")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")

class TableStructure(BaseModel):
    """Table structure information
    
    Attributes:
        columns: Number of columns, must be greater than 0
        has_header: Whether the table has a header row
    """
    columns: int = Field(gt=0, description="Number of columns")
    has_header: bool = Field(description="Whether the table has a header row")

# Action Classes
class MergeAction(BaseModel):
    """Merge action - Describes content that needs to be merged
    
    Attributes:
        type: Merge type, currently only supports table
        pages: List of involved page numbers, must contain at least one page
        line_ranges: Line ranges for each page, keyed by page number string
        confidence: Confidence score (0.0-1.0)
        is_cross_page: Whether this is truly a cross-page merge
        table_structure: Table structure information
    """
    type: ContentType
    pages: List[int] = Field(min_length=1, description="List of involved page numbers")
    line_ranges: Dict[str, List[LineRange]]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    is_cross_page: bool = Field(default=False, description="Whether this is truly a cross-page merge")
    table_structure: Optional[TableStructure] = Field(default=None, description="Table structure information")

class RemoveAction(BaseModel):
    """Remove action - Describes content that needs to be removed
    
    Attributes:
        page: Page number, must be greater than 0
        lines: List of line numbers, must not be empty
        reason: Removal reason
        confidence: Confidence score (0.0-1.0)
    """
    page: int = Field(gt=0, description="Page number")
    lines: List[int] = Field(min_length=1, description="List of line numbers")
    reason: RemoveReason
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")

class Warning(BaseModel):
    """Warning information - Records processing anomalies
    
    Attributes:
        type: Warning type
        page: Page number, must be greater than 0
        lines: List of related line numbers, must not be empty
        message: Warning message, must not be empty
    """
    type: WarningType
    page: int = Field(gt=0, description="Page number")
    lines: List[int] = Field(min_length=1, description="List of related line numbers")
    message: str = Field(min_length=1, description="Warning message")

class DocumentDebugInfo(BaseModel):
    """Document debug information - Records overall statistics
    
    Attributes:
        total_pages: Total number of pages, must be greater than 0
        total_tables: Total number of tables, must be greater than or equal to 0
        total_images: Total number of images, must be greater than or equal to 0
        total_headings: Total number of headings, must be greater than or equal to 0
    """
    total_pages: int = Field(gt=0, description="Total number of pages")
    total_tables: int = Field(ge=0, description="Total number of tables")
    total_images: int = Field(ge=0, description="Total number of images")
    total_headings: int = Field(ge=0, description="Total number of headings")

class DocumentAnalysis(BaseModel):
    """Document analysis result - Integrates all analysis information
    
    Processing Priority Order:
    1. remove_actions: Handle headers/footers (highest reliability)
    2. heading_infos: Process basic headings (high reliability)
    3. merge_actions: Handle table merging (needs more processing)
    4. warnings: Record anomalies
    
    Attributes:
        debug_info: Debug information
        remove_actions: List of remove actions for headers/footers
        heading_infos: List of heading information
        merge_actions: List of merge actions for tables
        warnings: List of warnings
    """
    debug_info: DocumentDebugInfo
    remove_actions: List[RemoveAction] = Field(default_factory=list, description="List of remove actions for headers/footers")
    heading_infos: List[HeadingInfo] = Field(default_factory=list, description="List of heading information")
    merge_actions: List[MergeAction] = Field(default_factory=list, description="List of merge actions for tables")
    warnings: List[Warning] = Field(default_factory=list, description="List of warnings")

if __name__ == "__main__":
    # Ensure project root directory is used
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test data
    test_doc = {
        "debug_info": {
            "total_pages": 2,
            "total_tables": 1,
            "total_images": 0,
            "total_headings": 2
        },
        "heading_infos": [
            {
                "page": 1,
                "line": 1,
                "level": 1,
                "content": "Document Title",
                "confidence": 0.98
            },
            {
                "page": 1,
                "line": 5,
                "level": 2,
                "content": "Chapter 1",
                "confidence": 0.95
            }
        ],
        "remove_actions": [
            {
                "page": 1,
                "lines": [1, 2],
                "reason": "header",
                "confidence": 0.95
            },
            {
                "page": 2,
                "lines": [20],
                "reason": "footer",
                "confidence": 0.98
            }
        ],
        "merge_actions": [
            {
                "type": "table",
                "pages": [1, 2],
                "line_ranges": {
                    "1": [
                        {
                            "start": 10,
                            "end": 15,
                            "is_header": True,
                            "has_separator": True
                        }
                    ]
                },
                "confidence": 0.95,
                "is_cross_page": True,
                "table_structure": {
                    "columns": 3,
                    "has_header": True
                }
            }
        ]
    }
    
    # Validate document
    result = DocumentAnalysis.model_validate(test_doc)
    rich.print("Valid document analysis:", result)
    
    # Test invalid document
    invalid_doc = {
        "debug_info": {
            "total_pages": 1  # Missing necessary statistics
        }
    }
    try:
        DocumentAnalysis.model_validate(invalid_doc)
    except Exception as e:
        print("Expected validation error:", e) 