"""Markdown document content marker.

Main function:
Generates marked content for {marked_content_from_pages} in prompts.py.
Converts raw Markdown documents into a format with clear markers and boundaries.

Input format:
List[List[str]] - Document content organized by pages
Example: [
    ["page1 line1", "page1 line2"],
    ["page2 line1", "page2 line2"]
]

Output format:
Generates marked content with clear boundaries:

### BEGIN_DOCUMENT ###
=== PAGE 1 ===
[P1-L1] page1 line1
[P1-L2] page1 line2
=== END PAGE 1 ===

=== PAGE 2 ===
[P2-L1] page2 line1
[P2-L2] page2 line2
=== END PAGE 2 ===
### END_DOCUMENT ###
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo

@dataclass
class MarkdownPage:
    """Single page Markdown content"""
    page_num: int
    lines: List[str]
    
    def add_markers(self) -> str:
        """Add page and line markers"""
        result = [f"=== PAGE {self.page_num} ==="]
        for i, line in enumerate(self.lines, 1):
            result.append(f"[P{self.page_num}-L{i}] {line}")
        result.append(f"=== END PAGE {self.page_num} ===")
        return "\n".join(result)

class MarkedContentMaker:
    """Content marker for generating marked_content_from_pages in prompts.py"""
    
    @staticmethod
    def mark_page(page_num: int, content_lines: List[str]) -> MarkdownPage:
        """Mark a single page content"""
        return MarkdownPage(page_num=page_num, lines=content_lines)
    
    def make_marked_content(self, pages_content: List[List[str]]) -> str:
        """Generate complete marked content
        
        Args:
            pages_content: Document content, each element is a list of lines for one page
            
        Returns:
            str: Generated marked content for marked_content_from_pages in prompts.py
        """
        marked_pages = [
            self.mark_page(i + 1, content)
            for i, content in enumerate(pages_content)
        ]
        
        result = ["### BEGIN_DOCUMENT ###"]
        for page in marked_pages:
            result.append(page.add_markers())
        result.append("### END_DOCUMENT ###")
        
        return "\n\n".join(result)
    
    def make_marked_content_from_md_info(self, md_info: MdInfo, fnames: Optional[List[str]] = None) -> Tuple[str, List[List[str]]]:
        doc_pages = []
        if fnames is None:
            fnames = md_info.get_fnames_pages()
        for fname in fnames:
            pname = os.path.join(md_info.get_out_dir(), fname)
            with open(pname, "r", encoding="utf-8") as f:
                content = f.readlines()
                doc_pages.append(content)
        return self.make_marked_content(doc_pages), doc_pages

# Usage example
if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    import rich 

    setup_logger_handlers()

    pname_info = "_test/ctn2md_mrag___paged_md/_info.json"
    md_info = MdInfo(pname_info)

    # Generate marked content
    maker = MarkedContentMaker()
    marked_content, _ = maker.make_marked_content_from_md_info(md_info)
    print("Generated marked content (for marked_content_from_pages in prompts.py):")
    rich.print(marked_content) 