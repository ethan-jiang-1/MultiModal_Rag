"""
文档分析器 - 使用LLM分析整个文档结构
"""

from typing import List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.llm_heading.da_client_heading import llmClientHeading
from ctn2md.gen_base.page_md_fusion.llm_heading.da_prompts_heading import SYSTEM_PROMPT_DOC_ANALYSIS_HEADING, USER_PROMPT_DOC_ANALYSIS_HEADING
from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import DocumentAnalysisHeading
from ctn2md.gen_base.page_md_fusion.llm_heading.full_marked_content_maker import FullMarkedContentMaker
from ctn2md.gen_base.page_md_fusion.llm_heading.heading_action_explainer import HeadingActionExplainer

logger = logging.getLogger(__name__)

class DocumentHeadingAnalyzer:
    """文档分析器：生成文档结构分析"""
    
    def __init__(self, md_info: MdInfo, using_cache: bool = True, debug: bool = False):
        self.md_info = md_info
        self.llm_client = llmClientHeading(md_info, using_cache=using_cache)
        self.debug = debug
  
    def analyze(self, fnames: Optional[List[str]] = None, debug: bool = False) -> DocumentAnalysisHeading:
        """分析文档并生成动作指令"""
        # 1. 准备带标记的文档内容
        mcm = FullMarkedContentMaker()
        marked_content, doc_pages = mcm.make_marked_content_from_md_info(self.md_info, fnames)
        
        system_prompt = SYSTEM_PROMPT_DOC_ANALYSIS_HEADING
        user_prompt = USER_PROMPT_DOC_ANALYSIS_HEADING.replace("{marked_content_from_pages}", marked_content)

        # 2. 调用LLM分析
        das = self.llm_client.analyze_document(system_prompt, user_prompt)
        
        # 3. 修复heading_id格式
        if das and das.headings:
            for i, heading in enumerate(das.headings, 1):
                heading.heading_id = str(i)
                if heading.validation and heading.validation.context:
                    if i > 1:
                        heading.validation.context.prev_heading_id = str(i-1)
                    else:
                        heading.validation.context.prev_heading_id = None
        
        # 4. 生成分析报告
        if self.debug:
            explanation = HeadingActionExplainer(das).explain()
            logger.info("\nDocument Analysis Report:\n%s", explanation)
        
        return das

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    import rich

    setup_logger_handlers()
    
    # 测试代码
    pname_info = "_test/ctn2md_papers___paged_md/_info.json"
    #pname_info = "_test/ctn2md_mrag___paged_md/_info.json"
    md_info = MdInfo(pname_info)
    
    analyzer = DocumentHeadingAnalyzer(md_info, using_cache=False, debug=True)  # 使用md_info初始化
    fnames = md_info.get_fnames_pages()  # 只测试前3页
    result = analyzer.analyze(fnames)
    
    # 打印分析结果
    rich.print("\nDocument Analysis Object:")
    rich.print(result) 