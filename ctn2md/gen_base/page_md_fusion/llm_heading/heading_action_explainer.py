"""
Document Analysis Result Explainer - Convert DocumentAnalysis objects to readable report format
"""

from typing import List # , Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading, 
    #ValidationScope,
    HeadingErrorType,
    ContentType,
    HeadingInfo,
    #HeadingValidation,
    TableStructure,
    LineRange
)

logger = logging.getLogger(__name__)

class HeadingActionExplainer:
    """Document analysis result explainer"""
    
    @staticmethod
    def get_line_preview(doc_pages: List[List[str]], page: int, line: int) -> str:
        """Get preview content for specified line"""
        try:
            return doc_pages[page - 1][line - 1][:100]  # Show more content for better understanding
        except (IndexError, TypeError):
            return "<line not found>"
            
    @staticmethod
    def explain_table_structure(action: TableStructure) -> List[str]:
        """Explain table structure"""
        lines = []
        if action.table_structure:
            lines.append(f"  ├─ Columns: {action.table_structure.columns}")
            lines.append(f"  ├─ Has Header: {'Yes' if action.table_structure.has_header else 'No'}")
        return lines
            
    @staticmethod
    def explain_table_range(range_info: LineRange) -> str:
        """Explain table range information"""
        parts = []
        if range_info.is_header:
            parts.append("Header")
        if range_info.has_separator:
            parts.append("Has Separator")
        return f"({', '.join(parts)})" if parts else ""

    @staticmethod
    def explain_heading_validation(heading: HeadingInfo) -> List[str]:
        """Explain heading validation results and suggest actions"""
        lines = []
        validation = heading.validation
        
        # Clean heading content - remove trailing punctuation
        clean_content = heading.content.rstrip('。.，,')
        
        # Basic validation info
        lines.append(f"  ├─ Valid: {'Yes' if validation.is_valid else 'No'}")
        lines.append(f"  ├─ Scope: {validation.validation_scope}")
        
        # Error details and required actions
        if not validation.is_valid and validation.error_type:
            lines.append(f"  ├─ Error: {validation.error_type}")
            
            # Suggest specific actions based on error type
            if validation.error_type == HeadingErrorType.WRONG_LEVEL:
                # Extract chapter info if available
                chapter_match = clean_content.split()[0]  # e.g. "14.3"
                parent_chapter = chapter_match.split('.')[0] if '.' in chapter_match else None
                
                if parent_chapter:
                    lines.append(f"  ├─ Action Required: Adjust heading level (sub-section of Chapter {parent_chapter})")
                else:
                    lines.append(f"  ├─ Action Required: Adjust heading level to match notation depth")
                
                if validation.expected_level:
                    current_markers = "#" * heading.level
                    expected_markers = "#" * validation.expected_level
                    lines.append(f"  ├─ Current Level: {heading.level}")
                    lines.append(f"  ├─ Expected Level: {validation.expected_level}")
                    lines.append(f"  ├─ Change: {current_markers} -> {expected_markers}")
                    lines.append(f"  ├─ From: {current_markers} {clean_content}")
                    lines.append(f"  ├─ To: {expected_markers} {clean_content}")
            
            elif validation.error_type == HeadingErrorType.WRONG_FORMAT:
                lines.append(f"  ├─ Action Required: Align notation with document structure")
                if validation.expected_content:
                    lines.append(f"  ├─ Current Format: {heading.content}")
                    lines.append(f"  ├─ Expected Format: {validation.expected_content}")
                    lines.append(f"  └─ Note: Maintain consistent delimiter usage")
            
            elif validation.error_type == HeadingErrorType.INCONSISTENT:
                lines.append(f"  ├─ Action Required: Fix structural inconsistency")
                if validation.expected_level:
                    lines.append(f"  ├─ Current Level: {heading.level}")
                    lines.append(f"  ├─ Expected Level: {validation.expected_level}")
                if validation.expected_content:
                    lines.append(f"  ├─ Expected Structure: {validation.expected_content}")
                lines.append(f"  └─ Note: Check parent-child relationship")
        
        return lines
            
    @classmethod
    def explain_document_analysis(cls, doc_analysis: DocumentAnalysisHeading, doc_pages: List[List[str]]) -> str:
        """Generate document analysis report
        
        Args:
            doc_analysis: Document analysis result
            doc_pages: Document page content
            
        Returns:
            Readable analysis report
        """
        lines = []
        
        # Document Statistics
        lines.append("📊 Document Statistics")
        lines.append("-" * 30)
        lines.append(f"• Total Pages: {doc_analysis.debug_info.total_pages}")
        lines.append(f"• Total Headings: {doc_analysis.debug_info.total_headings}")
        lines.append(f"• Total Tables: {doc_analysis.debug_info.total_tables}")
        lines.append(f"• Total Images: {doc_analysis.debug_info.total_images}")
        lines.append("")
        
        # Heading Information
        if doc_analysis.heading_infos:
            lines.append("📑 Heading Structure")
            lines.append("-" * 30)
            for heading in doc_analysis.heading_infos:
                lines.append(f"• Level {heading.level} Heading (Page {heading.page}, Line {heading.line})")
                lines.append(f"  ├─ Content: {heading.content}")
                lines.append(f"  ├─ Confidence: {heading.confidence * 100:.1f}%")
                # Add validation information
                lines.extend(cls.explain_heading_validation(heading))
            lines.append("")
        
        # Content Removal Actions
        if doc_analysis.remove_actions:
            lines.append("🗑️ Content Removal Actions")
            lines.append("-" * 30)
            for i, action in enumerate(doc_analysis.remove_actions, 1):
                lines.append(f"• Page {action.page} - Lines {action.lines}")
                lines.append(f"  ├─ Type: {action.reason.value}")
                lines.append(f"  ├─ Confidence: {action.confidence * 100:.1f}%")
                preview = cls.get_line_preview(doc_pages, action.page, action.lines[0])
                lines.append(f"  └─ Content: {preview}")
            lines.append("")
        
        # Content Merge Actions
        if doc_analysis.merge_actions:
            lines.append("🔄 Content Merge Actions")
            lines.append("-" * 30)
            for i, action in enumerate(doc_analysis.merge_actions, 1):
                lines.append(f"• Merge #{i}: {action.type.value}")
                lines.append(f"  ├─ Pages Involved: {action.pages}")
                lines.append(f"  ├─ Confidence: {action.confidence * 100:.1f}%")
                lines.append(f"  ├─ Cross-page Merge: {'Yes' if action.is_cross_page else 'No'}")
                
                # Add table structure information
                if action.type == ContentType.TABLE:
                    lines.extend(cls.explain_table_structure(action))
                
                # Show content range for each page
                for page, ranges in action.line_ranges.items():
                    for range_info in ranges:
                        range_desc = cls.explain_table_range(range_info)
                        lines.append(f"  ├─ Page {page}: Lines {range_info.start}-{range_info.end} {range_desc}")
                        start_preview = cls.get_line_preview(doc_pages, int(page), range_info.start)
                        end_preview = cls.get_line_preview(doc_pages, int(page), range_info.end)
                        lines.append(f"  │  ├─ Start: {start_preview}")
                        lines.append(f"  │  └─ End: {end_preview}")
            lines.append("")
        
        # Warnings
        if doc_analysis.warnings:
            lines.append("⚠️ Warnings")
            lines.append("-" * 30)
            for warning in doc_analysis.warnings:
                lines.append(f"• {warning.type.value} on Page {warning.page}")
                lines.append(f"  ├─ Lines: {warning.lines}")
                lines.append(f"  └─ Message: {warning.message}")
            lines.append("")
            
        return "\n".join(lines)

if __name__ == "__main__":
    # Test code with validation issues
    test_doc = {
        "debug_info": {
            "total_pages": 8,
            "total_tables": 1,
            "total_images": 0,
            "total_headings": 5
        },
        "heading_infos": [
            {
                "page": 1,
                "line": 1,
                "level": 1,
                "content": "深度学习在视电阻率快速反演中的研究与应用",
                "confidence": 0.98,
                "validation": {
                    "is_valid": True,
                    "validation_scope": "single_page"
                }
            },
            {
                "page": 2,
                "line": 1,
                "level": 1,
                "content": "0 引言",
                "confidence": 0.9,
                "validation": {
                    "is_valid": False,
                    "validation_scope": "cross_page",
                    "error_type": "wrong_level",
                    "expected_level": 2,
                    "expected_content": "1 引言"
                }
            },
            {
                "page": 4,
                "line": 1,
                "level": 2,
                "content": "14.3 地球物理开源程序 SimPEG",
                "confidence": 0.9,
                "validation": {
                    "is_valid": False,
                    "validation_scope": "cross_page",
                    "error_type": "wrong_format",
                    "expected_content": "1.3 地球物理开源程序 SimPEG"
                }
            },
            {
                "page": 5,
                "line": 1,
                "level": 1,
                "content": "2.2 ARESInvNet 网络结构",
                "confidence": 0.9,
                "validation": {
                    "is_valid": False,
                    "validation_scope": "cross_page",
                    "error_type": "inconsistent",
                    "expected_level": 2,
                    "expected_content": "2.2 ARESInvNet 网络结构"
                }
            },
            {
                "page": 6,
                "line": 2,
                "level": 2,
                "content": "<missing>",
                "confidence": 0.9,
                "validation": {
                    "is_valid": False,
                    "validation_scope": "cross_page",
                    "error_type": "missing",
                    "expected_content": "2.3 实验结果分析"
                }
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
    
    doc_pages = [
        ["[P1-L1] # 深度学习在视电阻率快速反演中的研究与应用"],
        ["[P2-L1] # 0 引言"],
        ["[P4-L1] ## 14.3 地球物理开源程序 SimPEG"],
        ["[P5-L1] # 2.2 ARESInvNet 网络结构"],
        ["[P6-L1] Content without heading"],
    ]
    
    # Test explanation
    doc_analysis = DocumentAnalysisHeading.model_validate(test_doc)
    explanation = HeadingActionExplainer.explain_document_analysis(doc_analysis, doc_pages)
    print(explanation) 