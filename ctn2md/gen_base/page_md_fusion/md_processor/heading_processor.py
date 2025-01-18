"""
标题处理器 - 处理文档标题结构
"""

from typing import List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
    HeadingInfo,
    HeadingErrorType
)

logger = logging.getLogger(__name__)

class HeadingProcessor:
    """标题处理器：处理文档标题结构"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象
        """
        self.md_info = md_info
            
    def process(self, pages_content: List[List[str]], doc_analysis: DocumentAnalysisHeading) -> Optional[List[List[str]]]:
        """处理标题结构
        
        Args:
            pages_content: 所有页面的内容
            doc_analysis: 文档分析结果
                
        Returns:
            处理后的页面内容,如果处理失败则返回None
        """
        try:
            # 1. 创建页面内容副本
            processed_pages = []
            for page in pages_content:
                processed_pages.append(page.copy())
            
            # 2. 处理标题
            for heading in doc_analysis.headings:
                page_idx = heading.page - 1
                line_idx = heading.line - 1
                
                # 2.1 根据验证结果处理标题
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
                        heading
                    )
                    
            # 3. 处理跨页问题
            if doc_analysis.structure_validation.cross_page_issues:
                processed_pages = self._handle_cross_page_issues(
                    processed_pages,
                    doc_analysis
                )
                
            return processed_pages
            
        except Exception as e:
            logger.error(f"Error during heading processing: {e}", exc_info=True)
            return None
            
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
        heading: HeadingInfo
    ) -> None:
        """处理无效标题
        
        Args:
            pages: 所有页面的内容
            heading: 标题信息(包含验证结果)
        """
        page_idx = heading.page - 1
        line_idx = heading.line - 1
        
        if heading.validation:
            if heading.validation.error_type == HeadingErrorType.LEVEL_TOO_DEEP:
                # 调整到合适的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.suggested_level
                )
                pages[page_idx][line_idx] = new_heading
                
            elif heading.validation.error_type == HeadingErrorType.LEVEL_TOO_SHALLOW:
                # 调整到合适的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.suggested_level
                )
                pages[page_idx][line_idx] = new_heading
                
            elif heading.validation.error_type == HeadingErrorType.INVALID_JUMP:
                # 调整到建议的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.suggested_level
                )
                pages[page_idx][line_idx] = new_heading
                
    def _handle_cross_page_issues(
        self,
        pages: List[List[str]],
        doc_analysis: DocumentAnalysisHeading
    ) -> List[List[str]]:
        """处理跨页问题
        
        Args:
            pages: 所有页面的内容
            doc_analysis: 文档分析结果
                
        Returns:
            处理后的页面内容
        """
        # TODO: 实现跨页问题处理逻辑
        return pages 