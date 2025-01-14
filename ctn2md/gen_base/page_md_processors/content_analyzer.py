from dotenv import load_dotenv
import os
#import logging
import re
from typing import List, Dict # , Tuple

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.gen_base.page_md_processors.base import BaseProcessor
from ctn2md.gen_base.page_md_processors.data_types import PageAnalysisResult

class ContentAnalyzer(BaseProcessor):
    """内容分析器：负责分析所有页面并生成分析结果"""
    
    def process(self, pages: List[str]) -> PageAnalysisResult:
        """分析所有页面内容"""
        return self.analyze_pages(pages)
    
    def analyze_pages(self, pages: List[str]) -> PageAnalysisResult:
        """分析所有页面并返回分析结果"""
        # 1. 分析简单模式
        patterns = self._analyze_patterns(pages)
        
        # 2. LLM分析
        llm_results = self._analyze_with_llm(pages)
        
        # 3. 生成动作
        actions = self._generate_actions(patterns, llm_results)
        
        return PageAnalysisResult(
            simple_patterns=patterns,
            llm_analyzed=llm_results,
            page_actions=actions
        )
    
    def _analyze_patterns(self, pages: List[str]) -> Dict[str, List[str]]:
        """分析简单模式（页眉页脚等）"""
        headers = self._find_header_patterns(pages)
        footers = self._find_footer_patterns(pages)
        page_numbers = self._find_page_numbers(pages)
        
        return {
            'headers': headers,
            'footers': footers,
            'page_numbers': page_numbers
        }
    
    def _find_header_patterns(self, pages: List[str]) -> List[str]:
        """查找页眉模式"""
        header_candidates = []
        for page in pages:
            lines = self._read_page_content(page)
            if lines:
                # 取前3行作为候选
                header_candidates.append(lines[:3])
        
        # 分析重复模式
        return self._find_repeated_patterns(header_candidates)
    
    def _find_footer_patterns(self, pages: List[str]) -> List[str]:
        """查找页脚模式"""
        footer_candidates = []
        for page in pages:
            lines = self._read_page_content(page)
            if lines:
                # 取最后3行作为候选
                footer_candidates.append(lines[-3:])
        
        # 分析重复模式
        return self._find_repeated_patterns(footer_candidates)
    
    def _find_page_numbers(self, pages: List[str]) -> List[str]:
        """查找页码"""
        page_numbers = []
        for page in pages:
            lines = self._read_page_content(page)
            if lines:
                # 查找可能的页码
                for line in lines:
                    if self._is_page_number(line):
                        page_numbers.append(line)
        return page_numbers
    
    def _analyze_with_llm(self, pages: List[str]) -> Dict[str, Dict]:
        """使用LLM进行复杂分析"""
        return {
            'heading_hierarchy': self._analyze_headings(pages),
            'table_connections': self._analyze_tables(pages)
        }
    
    def _analyze_headings(self, pages: List[str]) -> Dict:
        """分析标题层级结构"""
        # TODO: 实现LLM调用来分析标题
        return {}
    
    def _analyze_tables(self, pages: List[str]) -> Dict:
        """分析表格连续性"""
        # TODO: 实现LLM调用来分析表格
        return {}
    
    def _generate_actions(self, patterns: Dict, llm_results: Dict) -> Dict[int, List[Dict]]:
        """根据分析结果生成需要执行的动作"""
        actions = {}
        for page_idx in range(len(patterns.get('headers', []))):
            page_actions = []
            
            # 添加页眉处理动作
            if patterns['headers']:
                page_actions.append({
                    'type': 'remove',
                    'target': 'header',
                    'position': {'lines': [0, 1, 2]},
                    'params': {'pattern': patterns['headers']}
                })
            
            # 添加页脚处理动作
            if patterns['footers']:
                page_actions.append({
                    'type': 'remove',
                    'target': 'footer',
                    'position': {'lines': [-3, -2, -1]},
                    'params': {'pattern': patterns['footers']}
                })
            
            if page_actions:
                actions[page_idx] = page_actions
                
        return actions
    
    def _read_page_content(self, page_path: str) -> List[str]:
        """读取页面内容"""
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            self.logger.error(f"Error reading page {page_path}: {e}")
            return []
    
    def _find_repeated_patterns(self, candidates: List[List[str]]) -> List[str]:
        """查找重复模式"""
        patterns = []
        if not candidates:
            return patterns
            
        # 简单的模式匹配：如果在多个页面中出现相同的行，认为是模式
        line_frequency = {}
        for page_lines in candidates:
            for line in page_lines:
                line = line.strip()
                if line:
                    line_frequency[line] = line_frequency.get(line, 0) + 1
        
        # 如果一个行在超过50%的页面中出现，认为是模式
        threshold = len(candidates) * 0.5
        patterns = [line for line, freq in line_frequency.items() 
                   if freq > threshold]
        
        return patterns
    
    def _is_page_number(self, line: str) -> bool:
        """判断是否是页码行"""
        # 简单的页码模式匹配
        line = line.strip()
        page_number_patterns = [
            r'^\d+$',                     # 纯数字
            r'^Page \d+$',                # "Page X"
            r'^第\s*\d+\s*页$',           # 中文页码
            r'^\d+/\d+$',                # "X/Y"格式
        ]
        
        return any(re.match(pattern, line) for pattern in page_number_patterns) 