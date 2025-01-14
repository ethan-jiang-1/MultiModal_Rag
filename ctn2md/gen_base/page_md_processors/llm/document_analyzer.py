"""
文档分析器 - 使用LLM分析整个文档结构
"""

from typing import List
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.base import BaseProcessor
from ctn2md.gen_base.page_md_processors.llm.client import LlmClient
from ctn2md.gen_base.page_md_processors.llm.prompts import get_document_analysis_prompt
from ctn2md.gen_base.page_md_processors.llm.schemas import DocumentAnalysis

logger = logging.getLogger(__name__)

class DocumentAnalyzer(BaseProcessor):
    """文档分析器：生成文档结构分析"""
    
    def __init__(self, md_info: MdInfo):
        super().__init__(md_info)
        self.llm_client = LlmClient()
    
    def analyze(self, pages: List[List[str]]) -> DocumentAnalysis:
        """分析文档并生成动作指令"""
        # 1. 准备带标记的文档内容
        marked_content = self._prepare_marked_content(pages)
        
        # 2. 构建分析提示
        prompt = get_document_analysis_prompt(marked_content)
        
        # 3. 调用LLM分析
        return self.llm_client.analyze_document(prompt)
    
    def _prepare_marked_content(self, pages: List[List[str]]) -> str:
        """准备带标记的文档内容"""
        document_content = ""
        
        for page_idx, page_lines in enumerate(pages, 1):
            document_content += f"\n<<<< 第{page_idx}页 >>>>\n"
            for line_idx, line in enumerate(page_lines, 1):
                document_content += f"[P{page_idx}-L{line_idx}] {line}\n"
            document_content += f"<<<< 第{page_idx}页 结束 >>>>\n"
        
        return document_content

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # 测试代码
    json_path = "_output/test_doc/_info.json"
    md_info = MdInfo.from_json(json_path)
    
    # 准备测试页面
    test_pages = [
        ["第一章 引言", "页眉内容", "正文内容"],
        ["表格内容", "页脚内容"]
    ]
    
    analyzer = DocumentAnalyzer(md_info)
    result = analyzer.analyze(test_pages)
    print(result.model_dump_json(indent=2, ensure_ascii=False)) 