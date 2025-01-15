"""
文档分析结果解释器 - 将DocumentAnalysis对象转换为可读的报告格式
"""

from typing import List
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.gen_base.page_md_processors.llm.da_schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

class ActionExplainer:
    """文档分析结果解释器"""
    
    @staticmethod
    def get_line_preview(doc_pages: List[List[str]], page: int, line: int) -> str:
        """获取指定行的预览内容"""
        try:
            return doc_pages[page - 1][line - 1][:100]  # 显示更多内容以便于理解
        except (IndexError, TypeError):
            return "<line not found>"
            
    @staticmethod
    def explain_table_structure(action) -> List[str]:
        """解释表格结构"""
        lines = []
        if action.table_structure:
            lines.append(f"  ├─ 列数: {action.table_structure.get('columns', '未知')}")
            lines.append(f"  ├─ 包含表头: {'是' if action.table_structure.get('has_header', False) else '否'}")
        return lines
            
    @staticmethod
    def explain_table_range(range_info) -> str:
        """解释表格范围信息"""
        parts = []
        if range_info.is_header:
            parts.append("表头")
        if range_info.has_separator:
            parts.append("含分隔符")
        return f"({', '.join(parts)})" if parts else ""
            
    @classmethod
    def explain_document_analysis(cls, doc_analysis: DocumentAnalysis, doc_pages: List[List[str]]) -> str:
        """生成文档分析报告
        
        Args:
            doc_analysis: 文档分析结果
            doc_pages: 文档页面内容
            
        Returns:
            可读的分析报告
        """
        lines = []
        
        # Document Statistics
        lines.append("📊 Document Statistics")
        lines.append("-" * 30)
        lines.append(f"• Total Pages: {doc_analysis.debug_info.total_pages}")
        
        # Page Statistics
        for page in doc_analysis.debug_info.pages:
            lines.append(f"\n• Page {page.page}:")
            lines.append(f"  ├─ Lines: {page.total_lines}")
            lines.append(f"  ├─ Headings: {page.heading_count}")
            lines.append(f"  ├─ Tables: {page.table_count}")
            lines.append(f"  ├─ Images: {page.image_count}")
            lines.append(f"  ├─ First Line: {page.first_line_preview}")
            lines.append(f"  └─ Last Line: {page.last_line_preview}")
        
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
                if hasattr(action, 'is_cross_page'):
                    lines.append(f"  ├─ 需要跨页合并: {'是' if action.is_cross_page else '否'}")
                
                # 添加表格结构信息
                if action.type == "table":
                    lines.extend(cls.explain_table_structure(action))
                
                # 显示每页的内容范围
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
                lines.append(f"• {warning.type} on Page {warning.page}")
                lines.append(f"  ├─ Lines: {warning.lines}")
                lines.append(f"  └─ Message: {warning.message}")
            lines.append("")
            
        return "\n".join(lines)

if __name__ == "__main__":
    # Test code
    # Create test data
    test_doc = {
        "debug_info": {
            "total_pages": 2,
            "pages": [
                {
                    "page": 1,
                    "total_lines": 20,
                    "heading_count": 2,
                    "table_count": 1,
                    "image_count": 0,
                    "first_line_preview": "[P1-L1] # Title",
                    "last_line_preview": "[P1-L20] End of page"
                }
            ]
        },
        "merge_actions": [
            {
                "type": "table",
                "pages": [1, 2],
                "line_ranges": {
                    "1": [
                        {
                            "start": 10,
                            "end": 15,
                            "content_type": "header",
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
        ["[P1-L1] # Title", "[P1-L2] Content"],
        ["[P2-L1] More content", "[P2-L2] The end"]
    ]
    
    # Test explanation
    doc_analysis = DocumentAnalysis.model_validate(test_doc)
    explanation = ActionExplainer.explain_document_analysis(doc_analysis, doc_pages)
    print(explanation) 