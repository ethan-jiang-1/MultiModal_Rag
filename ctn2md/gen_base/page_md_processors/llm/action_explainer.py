"""
文档分析结果解释器 - 将DocumentAnalysis对象转换为可读的报告格式
"""

from typing import List
import logging
from ctn2md.gen_base.page_md_processors.llm.da_schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

class ActionExplainer:
    """解释文档分析结果,生成格式化报告
    
    !!! IMPORTANT DESIGN NOTE - DO NOT DELETE !!!
    关于文档数据结构的重要说明:
    
    doc_pages: List[List[str]] 的具体含义:
    1. 外层List: 表示整个文档的所有页面的集合
    2. 内层List: 表示单个页面中的所有行
    3. str: 表示每一行的原始内容
    
    示例数据结构:
    doc_pages = [
        # 第1页
        [
            "# 深度学习在视电阻率快速反演中的研究与应用",  # 原始内容
            "",                                        # 空行
            "### 余传涛1,2，李子伦1，薛俊杰2,3,4*"      # 原始内容
        ],
        # 第2页
        [
            "# 0 引言",
            "",
            "电法勘探是煤炭领域含水结构体探测的主要手段..."
        ]
    ]
    
    特别注意:
    - 每行内容都是原始文本，不包含 [Px-Ly] 这样的标记
    - 页码和行号使用数组索引确定，外层列表索引+1为页码，内层列表索引+1为行号
    - 这种结构设计使得文档处理保持原始内容的纯净性，更适合后续处理和渲染
    """
    
    @staticmethod
    def get_line_preview(doc_pages: List[List[str]], page_num: int, line_num: int) -> str:
        """Get preview of a specific line from doc_pages.
        
        !!! IMPORTANT - DO NOT MODIFY WITHOUT UNDERSTANDING !!!
        Args:
            doc_pages: 文档页面集合，其中:
                      - 外层列表的每个元素是一个页面
                      - 内层列表的每个元素是该页面的一行原始文本
                      - 文本内容不包含行号标记，保持原始格式
            page_num: 1-indexed 页码
            line_num: 1-indexed 行号
            
        Returns:
            First 32 chars of the line or error message if line not found
            
        Example:
            doc_pages = [
                ["# 标题", "", "正文内容"],  # 第1页
                ["## 小节", "", "更多内容"]   # 第2页
            ]
            get_line_preview(doc_pages, 1, 1) -> "# 标题"
        """
        # Convert to 0-based indexing
        page_idx = page_num - 1
        
        # Check if page exists
        if page_idx < 0 or page_idx >= len(doc_pages):
            return f"[page {page_num} not found]"
        
        # Get the page content
        page_content = doc_pages[page_idx]
        
        # Convert to 0-based line index
        line_idx = line_num - 1
        if line_idx < 0 or line_idx >= len(page_content):
            return f"[line {line_num} not found on page {page_num}]"
        return page_content[line_idx][:32]

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
    def explain_document_analysis(cls, doc_analysis: DocumentAnalysis, doc_pages: List[List[str]]) -> str:
        """Generate a formatted explanation of document analysis results.
        
        Args:
            doc_analysis: The document analysis results
            doc_pages: List of page contents where each page is a list of lines
            
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