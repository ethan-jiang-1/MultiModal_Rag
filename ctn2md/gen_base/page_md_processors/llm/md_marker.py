"""Markdown 文档标记器。

主要功能：
1. 为 Markdown 文档添加页号和行号标记
2. 生成符合 LLM 分析要求的格式化内容

标记格式：
- 页面边界：<<<< 第x页 >>>> 和 <<<< 第x页 结束 >>>>
- 行标记：[Px-Lx] 其中 x 是页号和行号
"""

from typing import List
from dataclasses import dataclass

@dataclass
class MarkdownPage:
    """单页 Markdown 内容"""
    page_num: int
    lines: List[str]
    
    def add_markers(self) -> str:
        """添加页面和行号标记"""
        result = [f"<<<< 第{self.page_num}页 >>>>"]
        for i, line in enumerate(self.lines, 1):
            result.append(f"[P{self.page_num}-L{i}] {line}")
        result.append(f"<<<< 第{self.page_num}页 结束 >>>>")
        return "\n".join(result)

class MarkdownMarker:
    """Markdown 标记处理器"""
    
    @staticmethod
    def mark_page(page_num: int, content_lines: List[str]) -> MarkdownPage:
        """标记单个页面"""
        return MarkdownPage(page_num=page_num, lines=content_lines)
    
    @staticmethod
    def combine_marked_pages(pages: List[MarkdownPage]) -> str:
        """组合多个已标记的页面"""
        return "\n\n".join(page.add_markers() for page in pages)
    
    def mark_document(self, pages_content: List[List[str]]) -> str:
        """标记整个文档
        
        Args:
            pages_content: 文档内容，每个元素是一页的行列表
            
        Returns:
            str: 添加了标记的文档内容
        """
        marked_pages = [
            self.mark_page(i + 1, content)
            for i, content in enumerate(pages_content)
        ]
        return self.combine_marked_pages(marked_pages)

# 使用示例
if __name__ == "__main__":
    # 示例文档（两页）
    doc_content = [
        # 第一页
        [
            "文档标题",
            "",
            "# 第一章",
            "正文内容...",
            "第 1 页"
        ],
        # 第二页
        [
            "文档标题",
            "正文继续...",
            "第 2 页"
        ]
    ]
    
    # 添加标记
    marker = MarkdownMarker()
    marked_content = marker.mark_document(doc_content)
    print(marked_content) 