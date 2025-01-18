"""
标题处理器 - 处理文档标题结构
"""

from typing import List, Optional
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
    HeadingInfo,
    HeadingErrorType,
    HeadingValidation,
    HeadingValidationScope,
    HeadingStructureValidation
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
            if heading.validation.error_type == HeadingErrorType.WRONG_LEVEL:
                # 调整到合适的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.expected_level
                )
                pages[page_idx][line_idx] = new_heading
                
            elif heading.validation.error_type == HeadingErrorType.NEEDS_LEVEL:
                # 调整到合适的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.expected_level
                )
                pages[page_idx][line_idx] = new_heading
                
            elif heading.validation.error_type == HeadingErrorType.WRONG_FORMAT:
                # 调整到建议的层级
                new_heading = self._format_heading(
                    heading.content,
                    heading.validation.expected_level
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

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    from ctn2md.md_info.md_info_base import MIFN
    from ctn2md.md_info.md_info_ctrl import _MIB_INFO_VER
    
    # 设置日志
    setup_logger_handlers()
    logger.info("Starting heading processor test...")
    
    # 准备测试目录和MdInfo
    test_dir = "_output/test_heading"
    info_path = os.path.join(test_dir, "_info.json")
    os.makedirs(test_dir, exist_ok=True)
    
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump({
            MIFN.VERSION: _MIB_INFO_VER,
            MIFN.GEN_ENGINE: "test",
            MIFN.DOC_UNIQUE_ID: "test_123",
            MIFN.FNAMES_MD_PAGES: ["page_1.md", "page_2.md"]
        }, f, ensure_ascii=False, indent=2)
    
    # 创建测试数据
    test_pages = [
        [  # 第1页 - 正常标题和错误标题
            "# 1. 系统概述",
            "#### 1.1 系统目标",  # 层级错误，应该是二级标题
            "系统目标包括：",
            "1. 提高效率"
        ],
        [  # 第2页 - 格式错误
            "2. 系统架构",  # 缺少标题标记
            "系统架构如下：",
            "- 三层架构"
        ]
    ]
    
    # 构造文档分析结果
    doc_analysis = DocumentAnalysisHeading(
        headings=[
            HeadingInfo(  # 正常标题
                page=1, line=1,
                content="1. 系统概述",
                heading_id="1",
                current_level=1,
                expected_level=1,
                confidence=0.98,
                validation=HeadingValidation(
                    is_valid=True,
                    current_level=1,
                    expected_level=1,
                    validation_scope=HeadingValidationScope.SINGLE_PAGE,
                    confidence=0.98
                )
            ),
            HeadingInfo(  # 层级错误
                page=1, line=2,
                content="1.1 系统目标",
                heading_id="2",
                current_level=4,
                expected_level=2,
                confidence=0.95,
                validation=HeadingValidation(
                    is_valid=False,
                    current_level=4,
                    expected_level=2,
                    error_type=HeadingErrorType.WRONG_LEVEL,
                    validation_scope=HeadingValidationScope.SINGLE_PAGE,
                    confidence=0.95
                )
            ),
            HeadingInfo(  # 格式错误
                page=2, line=1,
                content="2. 系统架构",
                heading_id="3",
                current_level=None,
                expected_level=1,
                confidence=0.90,
                validation=HeadingValidation(
                    is_valid=False,
                    current_level=None,
                    expected_level=1,
                    error_type=HeadingErrorType.WRONG_FORMAT,
                    validation_scope=HeadingValidationScope.SINGLE_PAGE,
                    confidence=0.90
                )
            )
        ],
        structure_validation=HeadingStructureValidation(
            is_valid=True,
            missing_levels=[],
            level_gaps=[],
            cross_page_issues=[]
        ),
        warnings=[],
        total_pages=2,
        total_headings=3
    )
    
    # 处理标题
    md_info = MdInfo(info_path)
    processor = HeadingProcessor(md_info)
    result = processor.process(test_pages, doc_analysis)
    
    # 打印结果
    if result:
        logger.info("Processing completed successfully")
        for idx, (orig, proc) in enumerate(zip(test_pages, result), 1):
            print(f"\n=== 第{idx}页 ===")
            print("原始：\n" + "\n".join(orig))
            print("\n处理后：\n" + "\n".join(proc))
            changes = len([i for i, (o, p) in enumerate(zip(orig, proc)) if o != p])
            logger.info(f"Page {idx}: {changes} lines changed")
    else:
        logger.error("Processing failed!") 