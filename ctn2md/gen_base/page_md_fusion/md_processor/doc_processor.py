"""
文档处理协调器 - 协调分析和执行流程
"""

from typing import List
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.md_processor.base import BaseProcessor
from ctn2md.gen_base.page_md_fusion.llm_heading.document_heading_analyzer import DocumentHeadingAnalyzer
from ctn2md.gen_base.page_md_fusion.md_processor.header_footer import HeaderFooterProcessor
from ctn2md.gen_base.page_md_fusion.md_processor.heading_processor import HeadingProcessor

logger = logging.getLogger(__name__)

class DocProcessor(BaseProcessor):
    """文档处理协调器：协调分析和执行流程"""
    
    def __init__(self, md_info: MdInfo):
        super().__init__(md_info)
        self.document_analyzer = DocumentHeadingAnalyzer(md_info)
        
        # 初始化处理器
        self.heading_processor = HeadingProcessor(md_info)
        self.header_footer_processor = HeaderFooterProcessor(md_info)
        
    def process_document(self, pages: List[List[str]]) -> List[List[str]]:
        """处理整个文档
        
        Args:
            pages: 所有页面的内容
            
        Returns:
            处理后的页面内容
        """
        # 1. 准备工作目录
        fusion_dir = self.md_info.get_aux_md_fusion_dir()
        os.makedirs(fusion_dir, exist_ok=True)
        
        # 复制原始文件到工作目录
        fusion_pages = []
        for i, page_content in enumerate(pages, 1):
            page_file = os.path.join(fusion_dir, f"page_{i}.md")
            with open(page_file, "w", encoding="utf-8") as f:
                f.write("\n".join(page_content))
            fusion_pages.append(page_file)
            
        # 2. LLM分析得到动作指令
        doc_analysis = self.document_analyzer.analyze()
        logger.info(f"Got document analysis: {doc_analysis}")
        
        # 3. 在工作目录中执行处理
        processed_pages = pages.copy()
        
        # 3.1 先处理标题结构（不改变行号）
        processed_pages = self.heading_processor.process(
            processed_pages,
            doc_analysis
        )
        
        # 3.2 再处理页眉页脚（会改变行号）
        processed_pages = self.header_footer_processor.process(
            processed_pages, 
            doc_analysis.remove_infos
        )
        
        # 4. 保存处理后的文件
        for i, page_content in enumerate(processed_pages, 1):
            page_file = os.path.join(fusion_dir, f"processed_page_{i}.md")
            with open(page_file, "w", encoding="utf-8") as f:
                f.write("\n".join(page_content))
        
        return processed_pages

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
            "正文内容",
            "| 表头1 | 表头2 |",
            "| --- | --- |",
            "| 数据1 | 数据2 |",
            "页脚"
        ],
        [  # 第2页
            "页眉",
            "| 数据3 | 数据4 |",
            "| 数据5 | 数据6 |",
            "正文继续",
            "页脚"
        ]
    ]
    
    # 测试处理
    processor = DocProcessor(md_info)
    result = processor.process_document(test_pages)
    
    # 打印结果
    for idx, page in enumerate(result, 1):
        print(f"\n=== 处理后的第{idx}页 ===")
        print("\n".join(page)) 