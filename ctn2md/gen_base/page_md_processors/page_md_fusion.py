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

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.doc_processor import DocProcessor
from ctn2md.gen_base.page_md_processors.base import prepare_md_fusion_workspace
from mmbase.utils.util_logging import setup_logger_handlers

logger = logging.getLogger(__name__)

class PageMdFusion:
    """页面MD融合的主控制器"""
    
    def __init__(self, md_info: MdInfo):
        """初始化
        
        Args:
            md_info: MD信息对象，包含页面文件列表等信息
        """
        self.md_info = md_info
        self.processor = DocProcessor(md_info)

    def process(self) -> bool:
        """执行融合处理流程
        
        Returns:
            处理是否成功
        """
        try:
            # 1. 准备工作空间
            logger.info("Preparing workspace...")
            pages = prepare_md_fusion_workspace(self.md_info)
            
            # 2. 处理文档
            logger.info("Processing document...")
            _ = self.processor.process_document(pages)  # 暂时不使用处理结果
            
            # 3. 保存更新
            logger.info("Saving results...")
            self.md_info.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during fusion process: {e}")
            return False

if __name__ == "__main__":
    # 设置日志
    setup_logger_handlers()
    
    # 测试融合处理
    json_path = "_output/test_doc/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    fusion = PageMdFusion(md_info)
    fusion.process() 