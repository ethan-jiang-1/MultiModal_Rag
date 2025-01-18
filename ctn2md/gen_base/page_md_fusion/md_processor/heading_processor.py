"""
标题处理器 - 处理文档标题结构
"""

from typing import List
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.md_processor.base import BaseProcessor
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
    HeadingInfo,
    HeadingStructureValidation,
    HeadingErrorType
)

logger = logging.getLogger(__name__)

class HeadingProcessor(BaseProcessor):
    """标题处理器：处理文档标题结构"""
    
    def __init__(self, md_info: MdInfo):
        super().__init__(md_info)
        
    def process(self, pages: List[List[str]], doc_analysis: DocumentAnalysisHeading) -> List[List[str]]:
        """处理标题结构
        
        Args:
            pages: 所有页面的内容
            doc_analysis: 文档分析结果
            
        Returns:
            处理后的页面内容
        """
        processed_pages = pages.copy()
        
        # 1. 处理标题
        for heading in doc_analysis.headings:
            page_idx = heading.page - 1
            line_idx = heading.line - 1
            
            # 1.1 根据验证结果处理标题
            if heading.validation and heading.validation.is_valid:
                # 调整标题格式
                new_heading = self._format_heading(
                    heading.content, 
                    heading.expected_level
                )
                processed_pages[page_idx][line_idx] = new_heading
            else:
                # 处理无效标题
                self._handle_invalid_heading(
                    processed_pages,
                    heading,
                    doc_analysis.structure_validation
                )
                
        # 2. 处理跨页问题
        if doc_analysis.structure_validation.cross_page_issues:
            processed_pages = self._handle_cross_page_issues(
                processed_pages,
                doc_analysis
            )
                
        return processed_pages
        
    def _format_heading(self, content: str, level: int) -> str:
        """格式化标题
        
        Args:
            content: 标题内容
            level: 标题层级
            
        Returns:
            格式化后的标题
        """
        prefix = "#" * level
        return f"{prefix} {content}"
        
    def _handle_invalid_heading(
        self, 
        pages: List[List[str]], 
        heading: HeadingInfo,
        structure_validation: HeadingStructureValidation
    ):
        """处理无效标题
        
        Args:
            pages: 页面内容
            heading: 标题信息
            structure_validation: 结构验证结果
        """
        if not heading.validation:
            return
            
        page_idx = heading.page - 1
        line_idx = heading.line - 1
        
        if heading.validation.error_type == HeadingErrorType.WRONG_LEVEL:
            # 调整标题层级
            new_heading = self._format_heading(
                heading.content,
                heading.validation.expected_level or heading.expected_level
            )
            pages[page_idx][line_idx] = new_heading
            
        elif heading.validation.error_type == HeadingErrorType.NOT_HEADING:
            # 移除标题格式
            pages[page_idx][line_idx] = heading.content.lstrip("#").strip()
            
        elif heading.validation.error_type == HeadingErrorType.WRONG_FORMAT:
            # 修复标题格式
            new_heading = self._format_heading(
                heading.content.lstrip("#").strip(),
                heading.expected_level
            )
            pages[page_idx][line_idx] = new_heading
            
    def _handle_cross_page_issues(
        self,
        pages: List[List[str]],
        doc_analysis: DocumentAnalysisHeading
    ) -> List[List[str]]:
        """处理跨页问题
        
        Args:
            pages: 页面内容
            doc_analysis: 文档分析结果
            
        Returns:
            处理后的页面内容
        """
        for issue in doc_analysis.structure_validation.cross_page_issues:
            # 获取相关标题
            heading = doc_analysis.headings[issue.heading_index]
            
            # 根据问题类型处理
            if issue.type == "break_heading":
                # 处理断开的标题
                self._handle_broken_heading(pages, heading, issue.start_page, issue.end_page)
            elif issue.type == "lost_context":
                # 处理丢失上下文的标题
                self._handle_lost_context(pages, heading, doc_analysis)
                
        return pages
        
    def _handle_broken_heading(
        self,
        pages: List[List[str]],
        heading: HeadingInfo,
        start_page: int,
        end_page: int
    ):
        """处理断开的标题
        
        Args:
            pages: 页面内容
            heading: 标题信息
            start_page: 起始页码
            end_page: 结束页码
        """
        # 实现处理断开标题的逻辑
        pass
        
    def _handle_lost_context(
        self,
        pages: List[List[str]],
        heading: HeadingInfo,
        doc_analysis: DocumentAnalysisHeading
    ):
        """处理丢失上下文的标题
        
        Args:
            pages: 页面内容
            heading: 标题信息
            doc_analysis: 文档分析结果
        """
        # 实现处理丢失上下文的逻辑
        pass 