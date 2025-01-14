from dotenv import load_dotenv
import os
from typing import List, Dict, Tuple, Optional

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.gen_base.page_md_processors.base import BaseProcessor

class TableMergerProcessor(BaseProcessor):
    """表格合并处理器：负责处理跨页表格"""
    
    def process(self, current_page: List[str], next_page: List[str], 
               table_info: Dict) -> Tuple[List[str], List[str]]:
        """处理跨页表格
        
        Args:
            current_page: 当前页内容
            next_page: 下一页内容
            table_info: 表格相关信息
        
        Returns:
            处理后的当前页和下一页内容
        """
        # 检查是否需要合并
        if not self._needs_merge(current_page, next_page, table_info):
            return current_page, next_page
        
        # 提取表格部分
        current_table = self._extract_table(current_page)
        next_table = self._extract_table(next_page)
        
        if not current_table or not next_table:
            return current_page, next_page
        
        # 合并表格
        merged_table = self._merge_tables(current_table, next_table)
        
        # 更新页面内容
        new_current = self._update_page_content(current_page, merged_table, 'current')
        new_next = self._update_page_content(next_page, merged_table, 'next')
        
        return new_current, new_next
    
    def _needs_merge(self, current_page: List[str], 
                    next_page: List[str], 
                    table_info: Dict) -> bool:
        """判断是否需要合并表格"""
        # 检查表格信息中的合并标记
        if not table_info.get('table_connections'):
            return False
            
        # 检查当前页是否包含未完成的表格
        current_has_table = self._has_incomplete_table_end(current_page)
        # 检查下一页是否包含表格开始
        next_has_table = self._has_table_start(next_page)
        
        return current_has_table and next_has_table
    
    def _has_incomplete_table_end(self, content: List[str]) -> bool:
        """检查是否有未完成的表格结尾"""
        if not content:
            return False
            
        # 检查最后几行
        for line in reversed(content[-3:]):
            if '|' in line and '-' not in line:
                return True
        return False
    
    def _has_table_start(self, content: List[str]) -> bool:
        """检查是否有表格开始"""
        if not content:
            return False
            
        # 检查开始几行
        for line in content[:3]:
            if '|' in line:
                return True
        return False
    
    def _extract_table(self, content: List[str]) -> Optional[List[str]]:
        """提取表格内容"""
        if not content:
            return None
            
        table_lines = []
        table_started = False
        
        for line in content:
            line = line.strip()
            if '|' in line:
                table_started = True
                table_lines.append(line)
            elif table_started and not line:
                # 空行标志着表格结束
                break
                
        return table_lines if table_lines else None
    
    def _merge_tables(self, current_table: List[str], 
                     next_table: List[str]) -> List[str]:
        """合并两个表格"""
        # 移除可能重复的表头
        if self._is_header_row(next_table[0]):
            next_table = next_table[1:]
        if self._is_separator_row(next_table[0]):
            next_table = next_table[1:]
            
        # 合并内容
        merged = current_table + next_table
        
        self.logger.info(
            f"Merged tables: {len(current_table)} + {len(next_table)} = {len(merged)} rows"
        )
        
        return merged
    
    def _is_header_row(self, line: str) -> bool:
        """判断是否是表头行"""
        return '|' in line and not all(c in '|-' for c in line.replace('|', ''))
    
    def _is_separator_row(self, line: str) -> bool:
        """判断是否是分隔行"""
        return '|' in line and all(c in '|-' for c in line.replace('|', ''))
    
    def _update_page_content(self, content: List[str], 
                           merged_table: List[str], 
                           page_type: str) -> List[str]:
        """更新页面内容
        
        Args:
            content: 原始页面内容
            merged_table: 合并后的表格
            page_type: 'current' 或 'next'
        """
        new_content = []
        
        if page_type == 'current':
            # 对于当前页，保留到表格开始
            for line in content:
                if '|' in line:
                    break
                new_content.append(line)
            # 添加完整的合并表格
            new_content.extend(merged_table)
            
        else:  # next page
            # 对于下一页，跳过原表格部分
            skip_table = False
            for line in content:
                if '|' in line and not skip_table:
                    skip_table = True
                    continue
                if skip_table and not line.strip():
                    skip_table = False
                if not skip_table:
                    new_content.append(line)
        
        return new_content 