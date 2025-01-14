"""
页面MD融合模块

用于处理分页MD文档的智能融合，主要解决：
1. 表格跨页处理
2. 标题层级关系重建
3. 页眉页脚清理
"""

from dotenv import load_dotenv
import os
import logging
from typing import List, Optional

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.src.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors import (
    ContentAnalyzer,
    HeaderFooterProcessor,
    HeadingHierarchyProcessor,
    TableMergerProcessor,
    ActionExecutor,
    PageAnalysisResult
)
from mmbase.utils.util_logging import setup_logger_handlers

class PageMdFusion:
    """页面MD融合的主控制器"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象，包含页面文件列表等信息
        """
        self.md_info = md_info
        self.pages = md_info.get_fnames_pages()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._init_processors()

    def _init_processors(self):
        """初始化所有处理器"""
        self.analyzer = ContentAnalyzer()
        self.header_footer = HeaderFooterProcessor()
        self.heading = HeadingHierarchyProcessor()
        self.table = TableMergerProcessor()
        self.executor = ActionExecutor()

    def process(self) -> bool:
        """执行融合处理流程
        
        Returns:
            处理是否成功
        """
        try:
            # 1. 分析阶段
            self.logger.info("Starting analysis phase...")
            analysis = self.analyzer.process(self.pages)
            
            # 2. 处理阶段
            self.logger.info("Starting processing phase...")
            success = self._process_pages(analysis)
            if not success:
                return False
            
            # 3. 保存更新
            self.logger.info("Saving results...")
            self.md_info.save()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during fusion process: {e}")
            return False

    def _process_pages(self, analysis: PageAnalysisResult) -> bool:
        """处理所有页面
        
        Args:
            analysis: 分析结果
            
        Returns:
            处理是否成功
        """
        try:
            # 1. 处理页眉页脚
            self._process_headers_footers(analysis)
            
            # 2. 处理标题层级
            self._process_headings(analysis)
            
            # 3. 处理表格
            self._process_tables(analysis)
            
            # 4. 执行其他动作
            self._execute_remaining_actions(analysis)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing pages: {e}")
            return False

    def _process_headers_footers(self, analysis: PageAnalysisResult):
        """处理所有页面的页眉页脚"""
        for page_idx, page in enumerate(self.pages):
            content = self._read_page_content(page)
            if content:
                # 处理页眉页脚
                content = self.header_footer.process(
                    content,
                    analysis.simple_patterns
                )
                # 保存更新后的内容
                self._save_page_content(page, content)

    def _process_headings(self, analysis: PageAnalysisResult):
        """处理所有页面的标题层级"""
        for page_idx, page in enumerate(self.pages):
            content = self._read_page_content(page)
            if content:
                # 处理标题层级
                content = self.heading.process(
                    content,
                    analysis.llm_analyzed
                )
                # 保存更新后的内容
                self._save_page_content(page, content)

    def _process_tables(self, analysis: PageAnalysisResult):
        """处理跨页表格"""
        for page_idx in range(len(self.pages) - 1):
            current_page = self._read_page_content(self.pages[page_idx])
            next_page = self._read_page_content(self.pages[page_idx + 1])
            
            if current_page and next_page:
                # 处理表格
                new_current, new_next = self.table.process(
                    current_page,
                    next_page,
                    analysis.llm_analyzed
                )
                # 保存更新后的内容
                self._save_page_content(self.pages[page_idx], new_current)
                self._save_page_content(self.pages[page_idx + 1], new_next)

    def _execute_remaining_actions(self, analysis: PageAnalysisResult):
        """执行剩余的页面动作"""
        for page_idx, page in enumerate(self.pages):
            if page_actions := analysis.page_actions.get(page_idx):
                content = self._read_page_content(page)
                if content:
                    # 执行动作
                    content = self.executor.process(content, page_actions)
                    # 保存更新后的内容
                    self._save_page_content(page, content)

    def _read_page_content(self, page_path: str) -> Optional[List[str]]:
        """读取页面内容"""
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            self.logger.error(f"Error reading page {page_path}: {e}")
            return None

    def _save_page_content(self, page_path: str, content: List[str]) -> bool:
        """保存页面内容"""
        try:
            with open(page_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            return True
        except Exception as e:
            self.logger.error(f"Error saving page {page_path}: {e}")
            return False

if __name__ == "__main__":
    setup_logger_handlers()
    
    # 测试代码
    test_info_path = "_output/ctn2md_mrag__AIGC时代的人力资源管理进化(徐刚)_lvlm/_info.json"
    if os.path.exists(test_info_path):
        md_info = MdInfo(test_info_path)
        fusion = PageMdFusion(md_info)
        success = fusion.process()
        print(f"Fusion {'succeeded' if success else 'failed'}") 