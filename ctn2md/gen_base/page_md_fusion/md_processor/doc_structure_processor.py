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
from ctn2md.gen_base.page_md_fusion.md_processor.heading_processor import HeadingProcessor
from ctn2md.gen_base.page_md_fusion.md_processor.header_footer import HeaderFooterProcessor
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    DocumentAnalysisHeading,
    HeadingInfo,
    HeadingStructureValidation,
    HeadingRemoveInfo
)

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
            logger.info("Preparing workspace...")
            page_paths = prepare_workspace(self.md_info)
            
            # 2. 读取页面内容
            pages_content = load_pages_content(page_paths)
            if not pages_content:
                raise ValueError("Failed to load pages content")
            
            # 3. 处理标题
            logger.info("Processing headings...")
            pages_content = self.heading_processor.process(pages_content, doc_analysis)
            if not pages_content:
                raise ValueError("Failed to process headings")
                
            # 4. 处理页眉页脚
            logger.info("Processing headers and footers...")
            pages_content = self.header_footer_processor.process(pages_content, doc_analysis.remove_infos)
            if not pages_content:
                raise ValueError("Failed to process headers and footers")
                
            # 5. 保存结果
            logger.info("Saving results...")
            if not save_pages_content(page_paths, pages_content):
                raise ValueError("Failed to save results")
                
            return pages_content
            
        except Exception as e:
            logger.error(f"Error during document processing: {e}", exc_info=True)
            return None

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试代码
    json_path = "_output/test_doc/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    # 准备测试页面
    test_pages = [
        [  # 第1页
            "页眉",
            "# 一级标题",
            "正文内容",
            "## 二级标题",
            "| 表头1 | 表头2 |",
            "| --- | --- |",
            "| 数据1 | 数据2 |",
            "页脚"
        ],
        [  # 第2页
            "页眉",
            "### 三级标题",
            "| 数据3 | 数据4 |",
            "| 数据5 | 数据6 |",
            "正文继续",
            "页脚"
        ]
    ]
    
    # 构造文档分析结果
    test_doc_analysis = DocumentAnalysisHeading(
        headings=[
            HeadingInfo(
                page=1,
                line=2,
                content="一级标题",
                expected_level=1,
                validation=HeadingStructureValidation(is_valid=True)
            ),
            HeadingInfo(
                page=1,
                line=4,
                content="二级标题",
                expected_level=2,
                validation=HeadingStructureValidation(is_valid=True)
            ),
            HeadingInfo(
                page=2,
                line=2,
                content="三级标题",
                expected_level=3,
                validation=HeadingStructureValidation(is_valid=True)
            )
        ],
        remove_infos=[
            HeadingRemoveInfo(
                page=1,
                lines=[1, 8],
                reason="header"
            ),
            HeadingRemoveInfo(
                page=2,
                lines=[1, 6],
                reason="footer"
            )
        ],
        structure_validation=HeadingStructureValidation(is_valid=True)
    )
    
    # 测试处理
    processor = DocStructureProcessor(md_info)
    result = processor.process_document(test_doc_analysis)
    
    # 打印结果
    if result:
        for idx, page in enumerate(result, 1):
            print(f"\n=== 处理后的第{idx}页 ===")
            print("\n".join(page))
    else:
        print("处理失败") 