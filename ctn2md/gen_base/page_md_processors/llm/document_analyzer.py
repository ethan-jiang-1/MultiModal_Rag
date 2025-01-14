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
        
        system_prompt = SYSTEM_PROMPT_DOC_ANALYSIS
        user_prompt = USER_PROMPT_DOC_ANALYSIS.format(marked_content_from_pages=marked_content)

        # 3. 调用LLM分析
        return self.llm_client.analyze_document(system_prompt, user_prompt)
    

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    import rich

    setup_logger_handlers()
    
    # 测试代码
    pname_info = "_work/ctn2md_papers___paged_md/_info.json"
    
    # 创建测试数据
    test_content = """### BEGIN_DOCUMENT ###
=== PAGE 1 ===
[P1-L1] Document Title
[P1-L2] Author: John Doe
[P1-L3] Page 1
[P1-L4] | Header 1 | Header 2 |
[P1-L5] |----------|----------|
[P1-L6] | Data 1   | Data 2   |
=== END PAGE 1 ===

=== PAGE 2 ===
[P2-L1] Page 2
[P2-L2] | Data 3   | Data 4   |
[P2-L3] | Data 5   | Data 6   |
[P2-L4] Footer text
=== END PAGE 2 ===
### END_DOCUMENT ###"""

    analyzer = DocumentAnalyzer(None)  # We don't need md_info for this test
    result = analyzer.llm_client.analyze_document(
        SYSTEM_PROMPT_DOC_ANALYSIS,
        USER_PROMPT_DOC_ANALYSIS.format(marked_content_from_pages=test_content)
    )
    rich.print(result) 