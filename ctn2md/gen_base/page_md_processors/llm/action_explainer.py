"""
文档分析结果解释器 - 将DocumentAnalysis对象转换为可读的报告格式
"""

from typing import List
import logging
from ctn2md.gen_base.page_md_processors.llm.da_schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

class ActionExplainer:
    """解释文档分析结果,生成格式化报告"""
    
    @staticmethod
    def get_line_preview(doc_pages: List[str], page_num: int, line_num: int) -> str:
        """Get a preview of a specific line from the document pages.
        
        Args:
            doc_pages: List of page contents, where each element is the entire content of a page
            page_num: 1-indexed page number
            line_num: 1-indexed line number
            
        Returns:
            First 32 characters of the specified line, or error message if line not found
        """
        # Convert to 0-based indexing
        page_idx = page_num - 1
        
        # Check if page exists
        if page_idx < 0 or page_idx >= len(doc_pages):
            return f"[page {page_num} does not exist]"
            
        # Get page content and split into lines
        lines = doc_pages[page_idx].split('\n')
        
        # Find the line that starts with [Px-Ly]
        target_marker = f"[P{page_num}-L{line_num}]"
        for line in lines:
            if line.startswith(target_marker):
                return line[:32]
            
        return f"[line {line_num} not found on page {page_num}]"

    @staticmethod
    def format_section_header(title: str) -> str:
        """Format a section header with consistent styling.
        
        Args:
            title: The section title
            
        Returns:
            Formatted section header with separators
        """
        return f"\n{'-' * 30}\n{title}\n{'-' * 30}"

    @classmethod
    def explain_document_analysis(cls, doc_analysis: DocumentAnalysis, doc_pages: List[str]) -> str:
        """Generate a formatted explanation of document analysis results.
        
        Args:
            doc_analysis: The document analysis results
            doc_pages: List of page contents where each element is the entire content of a page, the first element is the page-1
            
        Returns:
            A formatted string explaining the analysis results
        """
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("📑 DOCUMENT ANALYSIS REPORT")
        lines.append("-" * 80)
        lines.append("")
        
        # Document Statistics
        lines.append("📊 Document Statistics")
        lines.append("-" * 30)
        total_headings = sum(page.heading_count for page in doc_analysis.debug_info.pages)
        total_tables = sum(page.table_count for page in doc_analysis.debug_info.pages)
        total_images = sum(page.image_count for page in doc_analysis.debug_info.pages)
        lines.append(f"• Pages: {doc_analysis.debug_info.total_pages:,}")
        lines.append(f"• Headings: {total_headings:,}")
        lines.append(f"• Tables: {total_tables:,}")
        lines.append(f"• Images: {total_images:,}")
        lines.append("")
        
        # Page Details
        lines.append("📄 Page Details")
        lines.append("-" * 30)
        for page in doc_analysis.debug_info.pages:
            lines.append(f"• Page {page.page}:")
            lines.append(f"  ├─ Lines: {page.total_lines:,}")
            lines.append(f"  ├─ Headings: {page.heading_count:,}")
            lines.append(f"  ├─ Tables: {page.table_count:,}")
            lines.append(f"  ├─ Images: {page.image_count:,}")
            lines.append(f"  ├─ First: {page.first_line_preview}")
            lines.append(f"  └─ Last: {page.last_line_preview}")
        lines.append("")
        
        # Content Removal Actions
        if doc_analysis.remove_actions:
            lines.append("🗑️ Content Removal Actions")
            lines.append("-" * 30)
            for i, action in enumerate(doc_analysis.remove_actions, 1):
                lines.append(f"• Page {action.page} - Lines {action.lines}")
                lines.append(f"  ├─ Type: {action.reason.title()}")
                lines.append(f"  ├─ Confidence: {action.confidence * 100:.1f}%")
                preview = cls.get_line_preview(doc_pages, action.page, action.lines[0])
                lines.append(f"  └─ Content: {preview}")
            lines.append("")
        
        # Content Merge Actions
        if doc_analysis.merge_actions:
            lines.append("🔄 Content Merge Actions")
            lines.append("-" * 30)
            for i, action in enumerate(doc_analysis.merge_actions, 1):
                lines.append(f"• Merge #{i}: {action.type.title()}")
                lines.append(f"  ├─ Pages Involved: {action.pages}")
                lines.append(f"  ├─ Confidence: {action.confidence * 100:.1f}%")
                for page, ranges in action.line_ranges.items():
                    for range_info in ranges:
                        lines.append(f"  ├─ Page {page}: Lines {range_info['start']}-{range_info['end']} ({range_info['content_type']})")
                        start_preview = cls.get_line_preview(doc_pages, int(page), range_info['start'])
                        end_preview = cls.get_line_preview(doc_pages, int(page), range_info['end'])
                        lines.append(f"  │  ├─ Start: {start_preview}")
                        lines.append(f"  │  └─ End: {end_preview}")
            lines.append("")
        
        # Warnings
        if doc_analysis.warnings:
            lines.append("⚠️ Warnings")
            lines.append("-" * 30)
            for i, warning in enumerate(doc_analysis.warnings, 1):
                lines.append(f"• Warning #{i}: {warning.type}")
                lines.append(f"  ├─ Location: Page {warning.page}, Lines {warning.lines}")
                lines.append(f"  ├─ Details: {warning.message}")
                if warning.lines:
                    preview = cls.get_line_preview(doc_pages, warning.page, warning.lines[0])
                    lines.append(f"  └─ Content: {preview}")
            lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("End of Analysis Report")
        lines.append("=" * 80)
        
        return "\n".join(lines) 