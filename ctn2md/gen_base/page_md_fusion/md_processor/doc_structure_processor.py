"""
文档结构处理器 - 协调标题和页眉页脚的处理
"""

from typing import List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.md_processor.base import (
    load_pages_content,
    save_pages_content,
    prepare_workspace
)
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import DocumentAnalysisHeading
from ctn2md.gen_base.page_md_fusion.md_processor.heading_processor import HeadingProcessor
from ctn2md.gen_base.page_md_fusion.md_processor.header_footer import HeaderFooterProcessor
from mmbase.utils.util_logging import setup_logger_handlers

logger = logging.getLogger(__name__)

class DocStructureProcessor:
    """文档结构处理器：协调标题和页眉页脚的处理"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象
        """
        self.md_info = md_info
        self.heading_processor = HeadingProcessor(md_info)
        self.header_footer_processor = HeaderFooterProcessor(md_info)
        
    def process_document(self, doc_analysis: DocumentAnalysisHeading) -> Optional[List[List[str]]]:
        """处理文档
        
        Args:
            doc_analysis: 文档分析结果
            
        Returns:
            处理后的页面内容,如果处理失败则返回None
        """
        try:
            # 1. 准备工作空间
            logger.info("Step 1: Preparing workspace...")
            page_paths = prepare_workspace(self.md_info)
            logger.info(f"Workspace prepared with {len(page_paths)} files")
            
            # 2. 读取页面内容
            logger.info("Step 2: Loading pages content...")
            pages_content = load_pages_content(page_paths)
            if not pages_content:
                logger.error("Failed to load pages content")
                raise ValueError("Failed to load pages content")
            logger.info(f"Loaded {len(pages_content)} pages")
            
            # 3. 处理标题
            logger.info("Step 3: Processing headings...")
            logger.info(f"Found {len(doc_analysis.headings)} headings to process")
            pages_content = self.heading_processor.process(pages_content, doc_analysis)
            if not pages_content:
                logger.error("Failed to process headings")
                raise ValueError("Failed to process headings")
            logger.info("Headings processed successfully")
                
            # 4. 处理页眉页脚
            logger.info("Step 4: Processing headers and footers...")
            logger.info(f"Found {len(doc_analysis.remove_infos)} items to remove")
            pages_content = self.header_footer_processor.process(pages_content, doc_analysis.remove_infos)
            if not pages_content:
                logger.error("Failed to process headers and footers")
                raise ValueError("Failed to process headers and footers")
            logger.info("Headers and footers processed successfully")
                
            # 5. 保存结果
            logger.info("Step 5: Saving results...")
            if not save_pages_content(page_paths, pages_content):
                logger.error("Failed to save results")
                raise ValueError("Failed to save results")
            logger.info(f"Results saved to {len(page_paths)} files")
                
            logger.info("Document processing completed successfully")
            return pages_content
            
        except Exception as e:
            logger.error(f"Error during document processing: {str(e)}", exc_info=True)
            return None

if __name__ == "__main__":
    from ctn2md.md_info.md_info_base import MdInfo
    from ctn2md.gen_base.page_md_fusion.llm_heading.document_heading_analyzer import DocumentHeadingAnalyzer

    setup_logger_handlers()

    # 创建测试实例
    md_info = MdInfo("_test/ctn2md_papers___paged_md")
    doc_processor = DocStructureProcessor(md_info)
    doc_analyzer = DocumentHeadingAnalyzer(md_info)

    # 分析文档
    logger.info("Analyzing document...")
    doc_analysis = doc_analyzer.analyze()
    
    # 处理文档
    logger.info("Processing document...")
    processed_pages = doc_processor.process_document(doc_analysis)

    logger.info("Test completed successfully.") 