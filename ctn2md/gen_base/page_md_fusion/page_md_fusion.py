"""
页面MD融合模块

用于处理分页MD文档的智能融合，主要解决：
1. 表格跨页处理
2. 页眉页脚清理
"""

from dotenv import load_dotenv
import os
import logging

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.document_heading_analyzer import DocumentHeadingAnalyzer
from ctn2md.gen_base.page_md_fusion.md_processor.doc_structure_processor import DocStructureProcessor

logger = logging.getLogger(__name__)

class PageMdFusion:
    """页面MD融合的主控制器"""
    
    def __init__(self, md_info: MdInfo, debug: bool = False):
        """初始化
        
        Args:
            md_info: MD信息对象，包含页面文件列表等信息
        """
        self.md_info = md_info
        self.debug = debug
        self.document_analyzer = DocumentHeadingAnalyzer(md_info, debug)
        self.processor = DocStructureProcessor(md_info, debug)

    def process(self) -> bool:
        """执行融合处理流程
        
        Returns:
            处理是否成功
        """
        try:
            # 1. 分析文档结构
            logger.info("Analyzing document structure...")
            doc_analysis = self.document_analyzer.analyze()
            if not doc_analysis:
                raise ValueError("Document analysis failed")
            
            # 2. 处理文档
            logger.info("Processing document...")
            processed_pages = self.processor.process_document(doc_analysis)
            if processed_pages is None:
                raise ValueError("Document processing failed")
            
            # 3. 保存更新
            logger.info("Saving results...")
            self.md_info.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during fusion process: {e}", exc_info=True)
            return False

if __name__ == "__main__":
    # 设置日志
    setup_logger_handlers()
    
    # 测试文档路径
    #pname_info = "_test/ctn2md_papers___paged_md/_info.json"  # 使用正确的测试路径
    pname_info = "_test/ctn2md_papers___paged_md"
    md_info = MdInfo(pname_info)  # 直接使用构造函数
    
    fusion = PageMdFusion(md_info, debug=True)
    fusion.process() 