"""
MD处理器结果说明 - 用于展示处理后的文档结构
"""

from typing import List, Dict, Tuple
import re
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import DocumentAnalysisHeading

class MdProcessorExplainer:
    """MD处理器结果说明：展示处理后的文档结构"""
    
    def __init__(self, pages_content: List[List[str]], doc_analysis: DocumentAnalysisHeading):
        """初始化
        
        Args:
            pages_content: 处理后的页面内容
            doc_analysis: 文档分析结果
        """
        self.pages_content = pages_content
        self.doc_analysis = doc_analysis
        
    def _extract_headings(self) -> List[Tuple[int, int, str, int]]:
        """从处理后的内容中提取标题
        
        Returns:
            标题列表，每个元素为 (页码, 行号, 标题内容, 层级)
        """
        headings = []
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for page_idx, page in enumerate(self.pages_content, 1):
            for line_idx, line in enumerate(page, 1):
                match = heading_pattern.match(line)
                if match:
                    level = len(match.group(1))
                    content = match.group(2)
                    headings.append((page_idx, line_idx, content, level))
                    
        return headings
        
    def _format_toc(self, headings: List[Tuple[int, int, str, int]]) -> str:
        """格式化目录结构
        
        Args:
            headings: 标题列表
            
        Returns:
            格式化的目录字符串
        """
        toc_lines = ["目录结构："]
        
        for page, line, content, level in headings:
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- {content} (第{page}页, 第{line}行)")
            
        return "\n".join(toc_lines)
        
    def _summarize_removals(self) -> str:
        """总结移除的页眉页脚
        
        Returns:
            移除总结字符串
        """
        if not self.doc_analysis.remove_infos:
            return "未移除任何页眉页脚"
            
        removals_by_type: Dict[str, List[Tuple[int, List[int]]]] = {
            "header": [],
            "footer": [],
            "separator": []
        }
        
        for info in self.doc_analysis.remove_infos:
            removals_by_type[info.reason].append((info.page, info.lines))
            
        summary_lines = ["移除内容总结："]
        
        for reason, removals in removals_by_type.items():
            if removals:
                type_desc = {
                    "header": "页眉",
                    "footer": "页脚",
                    "separator": "分隔符"
                }[reason]
                
                pages = sorted(set(page for page, _ in removals))
                total_lines = sum(len(lines) for _, lines in removals)
                
                summary_lines.append(f"\n{type_desc}:")
                summary_lines.append(f"- 影响页面: {len(pages)} 页 ({', '.join(map(str, pages))})")
                summary_lines.append(f"- 移除行数: {total_lines} 行")
                
        return "\n".join(summary_lines)
        
    def explain(self) -> str:
        """生成处理结果说明
        
        Returns:
            处理结果说明字符串
        """
        parts = []
        
        # 1. 提取并格式化目录
        headings = self._extract_headings()
        parts.append(self._format_toc(headings))
        
        # 2. 总结移除的内容
        parts.append("\n\n" + self._summarize_removals())
        
        return "\n".join(parts) 