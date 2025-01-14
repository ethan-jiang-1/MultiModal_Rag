from dotenv import load_dotenv
import os
# import logging
from typing import List, Dict

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.gen_base.page_md_processors.base import BaseProcessor

class HeaderFooterProcessor(BaseProcessor):
    """页眉页脚处理器：负责清理页眉页脚"""
    
    def process(self, page_content: List[str], patterns: Dict) -> List[str]:
        """处理页眉页脚
        
        Args:
            page_content: 页面内容行列表
            patterns: 包含headers和footers的模式字典
        
        Returns:
            处理后的页面内容行列表
        """
        # 1. 清理页眉
        if patterns.get('headers'):
            page_content = self._remove_headers(page_content, patterns['headers'])
        
        # 2. 清理页脚
        if patterns.get('footers'):
            page_content = self._remove_footers(page_content, patterns['footers'])
        
        # 3. 处理页码（如果需要）
        if patterns.get('page_numbers'):
            page_content = self._handle_page_numbers(page_content, patterns['page_numbers'])
        
        return page_content
    
    def _remove_headers(self, content: List[str], header_patterns: List[str]) -> List[str]:
        """移除匹配的页眉"""
        if not content or not header_patterns:
            return content
        
        # 检查前几行
        header_end = 0
        for idx, line in enumerate(content[:3]):  # 只检查前3行
            line = line.strip()
            if any(pattern in line for pattern in header_patterns):
                header_end = idx + 1
        
        # 如果找到页眉，移除相应行数
        if header_end > 0:
            self.logger.info(f"Removing header lines 0-{header_end}")
            return content[header_end:]
        return content
    
    def _remove_footers(self, content: List[str], footer_patterns: List[str]) -> List[str]:
        """移除匹配的页脚"""
        if not content or not footer_patterns:
            return content
        
        # 检查最后几行
        footer_start = len(content)
        for idx in range(len(content)-1, max(len(content)-4, -1), -1):  # 只检查最后3行
            line = content[idx].strip()
            if any(pattern in line for pattern in footer_patterns):
                footer_start = idx
        
        # 如果找到页脚，移除相应行数
        if footer_start < len(content):
            self.logger.info(f"Removing footer lines {footer_start}-{len(content)}")
            return content[:footer_start]
        return content
    
    def _handle_page_numbers(self, content: List[str], page_patterns: List[str]) -> List[str]:
        """处理页码
        可以选择保留或移除页码，这里默认移除
        """
        if not content or not page_patterns:
            return content
        
        # 创建新的内容列表，排除页码行
        new_content = []
        for line in content:
            line_stripped = line.strip()
            if not any(pattern in line_stripped for pattern in page_patterns):
                new_content.append(line)
        
        return new_content 