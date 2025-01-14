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
    PageAnalysisResult,
    prepare_md_fusion_workspace
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
        self.pages = []  # 工作目录中的页面文件列表
        self.logger = logging.getLogger(self.__class__.__name__)
        self._init_processors()

    def _init_processors(self):
        """初始化所有处理器"""
        self.analyzer = ContentAnalyzer(self.md_info)
        self.header_footer = HeaderFooterProcessor(self.md_info)
        self.heading = HeadingHierarchyProcessor(self.md_info)
        self.table = TableMergerProcessor(self.md_info)
        self.executor = ActionExecutor(self.md_info)

    def process(self) -> bool:
        """执行融合处理流程
        
        Returns:
            处理是否成功
        """
        try:
            # 1. 准备工作空间
            self.logger.info("Preparing workspace...")
            self.pages = prepare_md_fusion_workspace(self.md_info)
            
            # 2. 分析阶段
            self.logger.info("Starting analysis phase...")
            analysis = self.analyzer.process(self.pages)
            
            # 3. 处理阶段
            self.logger.info("Starting processing phase...")
            success = self._process_pages(analysis)
            if not success:
                return False
            
            # 4. 保存更新
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
            self.header_footer.process(self.pages, analysis.simple_patterns)
            
            # 2. 处理标题层级
            self.heading.process(self.pages, analysis.llm_analyzed)
            
            # 3. 处理表格
            self.table.process(self.pages, analysis.llm_analyzed)
            
            # 4. 执行其他动作
            self.executor.process(self.pages, analysis.page_actions)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing pages: {e}")
            return False

if __name__ == "__main__":
    # 设置日志
    setup_logger_handlers()
    
    # 测试融合处理
    json_path = "_output/ctn2md_mrag__AIGC时代的人力资源管理进化(徐刚)_lvlm/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    fusion = PageMdFusion(md_info)
    fusion.process() 