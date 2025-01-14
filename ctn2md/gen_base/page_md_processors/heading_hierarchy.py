from dotenv import load_dotenv
import os
import re
from typing import List, Dict, Optional

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.gen_base.page_md_processors.base import BaseProcessor

class HeadingHierarchyProcessor(BaseProcessor):
    """标题层级处理器：负责分析和调整标题层级"""
    
    def process(self, page_content: List[str], hierarchy_info: Dict) -> List[str]:
        """处理标题层级
        
        Args:
            page_content: 页面内容行列表
            hierarchy_info: 标题层级信息，包含全局层级结构
        
        Returns:
            处理后的页面内容行列表
        """
        # 1. 识别当前页面的标题
        headings = self._identify_headings(page_content)
        
        # 2. 根据全局层级调整标题级别
        if headings:
            page_content = self._adjust_heading_levels(
                page_content, 
                headings,
                hierarchy_info
            )
        
        return page_content
    
    def _identify_headings(self, content: List[str]) -> List[Dict]:
        """识别页面中的标题行
        
        Returns:
            标题信息列表，每项包含：
            - line_number: 行号
            - text: 标题文本
            - level: 当前级别
            - original_line: 原始行内容
        """
        headings = []
        for idx, line in enumerate(content):
            if heading_info := self._parse_heading(line):
                heading_info['line_number'] = idx
                heading_info['original_line'] = line
                headings.append(heading_info)
        return headings
    
    def _parse_heading(self, line: str) -> Optional[Dict]:
        """解析标题行
        
        支持的格式：
        1. Markdown标题 (# 标题)
        2. 数字编号标题 (1. 标题)
        3. 中文编号标题 (一、标题)
        """
        line = line.strip()
        
        # Markdown标题
        if md_match := re.match(r'^(#{1,6})\s+(.+)$', line):
            return {
                'level': len(md_match.group(1)),
                'text': md_match.group(2).strip()
            }
        
        # 数字编号标题
        if num_match := re.match(r'^(\d+\.)+\s+(.+)$', line):
            level = len(num_match.group(1).split('.')) - 1
            return {
                'level': min(level, 6),
                'text': num_match.group(2).strip()
            }
        
        # 中文编号标题
        if cn_match := re.match(r'^[一二三四五六七八九十]+[、.]\s*(.+)$', line):
            return {
                'level': 1,  # 默认作为一级标题
                'text': cn_match.group(1).strip()
            }
        
        return None
    
    def _adjust_heading_levels(self, content: List[str], 
                             headings: List[Dict], 
                             hierarchy_info: Dict) -> List[str]:
        """调整标题级别以匹配全局层级结构"""
        if not headings or not hierarchy_info:
            return content
            
        # 创建新的内容列表
        new_content = content.copy()
        
        # 获取全局层级映射
        global_hierarchy = hierarchy_info.get('heading_hierarchy', {})
        
        # 调整每个标题的级别
        for heading in headings:
            line_number = heading['line_number']
            text = heading['text']
            
            # 查找全局层级中的对应关系
            if text in global_hierarchy:
                new_level = global_hierarchy[text]
                # 生成新的标题行
                new_heading = '#' * new_level + ' ' + text
                new_content[line_number] = new_heading
                
                self.logger.info(
                    f"Adjusted heading level for '{text}' "
                    f"from {heading['level']} to {new_level}"
                )
        
        return new_content 