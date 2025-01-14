"""
文档分析器 - 使用LLM分析整个文档结构
"""

from typing import List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.base import BaseProcessor
from ctn2md.gen_base.page_md_processors.llm.client import LlmClient
from ctn2md.gen_base.page_md_processors.llm.prompts import SYSTEM_PROMPT_DOC_ANALYSIS, USER_PROMPT_DOC_ANALYSIS
from ctn2md.gen_base.page_md_processors.llm.schemas import DocumentAnalysis
from ctn2md.gen_base.page_md_processors.llm.marked_content_maker import MarkedContentMaker

logger = logging.getLogger(__name__)

class DocumentAnalyzer(BaseProcessor):
    """文档分析器：生成文档结构分析"""
    
    def __init__(self, md_info: MdInfo):
        super().__init__(md_info)
        self.llm_client = LlmClient(md_info)
    
    def analyze(self, fnames: Optional[List[str]] = None) -> DocumentAnalysis:
        """分析文档并生成动作指令"""
        # 1. 准备带标记的文档内容
        marked_content = MarkedContentMaker().make_marked_content_from_md_info(self.md_info, fnames)
        
        system_prompt =SYSTEM_PROMPT_DOC_ANALYSIS
        user_prompt =USER_PROMPT_DOC_ANALYSIS.replace("{{marked_content_from_pages}}", marked_content)

        # 3. 调用LLM分析
        return self.llm_client.analyze_document(system_prompt, user_prompt)
    

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    import rich

    setup_logger_handlers()
    
    # 测试代码
    pname_info = "_work/ctn2md_papers___paged_md/_info.json"
    md_info = MdInfo(pname_info)

    fnames = md_info.get_fnames_pages()
    fnames = fnames[:3]

    # Generate marked content
    maker = MarkedContentMaker()
    marked_content = maker.make_marked_content_from_md_info(md_info, fnames)

    analyzer = DocumentAnalyzer(md_info)
    result = analyzer.analyze(fnames=None)
    rich.print(result) 