"""Document keywords generation implementation"""
from dotenv import load_dotenv
import rich

load_dotenv()

from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils_llm.llm_summarize_content import summarize_doc_keywords_by_llm
from ctn2md.src.summarize_content.doc_keywords import DocumentKeywords

def make_doc_keywords(md_info_path: str, doc_title: str, full_content: str) -> DocumentKeywords:
    """Generate document keywords using LLM analysis

    Args:
        md_info_path (str): Path to markdown info file
        doc_title (str): Document title
        full_content (str): Full document content

    Returns:
        DocumentKeywords: Structured data containing categorized keywords and summary
    """
    md_info = MdInfo(md_info_path)
    mctl_summarize_model = md_info.get_md_control("mctl_summarize_model", "gpt")
    if mctl_summarize_model == "gpt":
        model = "gpt-4o"
    elif mctl_summarize_model == "qwen":
        model = "qwen-plus"
    elif mctl_summarize_model == "ark":
        model = "ep-20241220101421-4tj5f"
    else:
        raise ValueError(f"not implemented yet for using {mctl_summarize_model} in sumamrize document")
    
    resp_dict = summarize_doc_keywords_by_llm(doc_title, full_content, model=model)
    rich.print(resp_dict)
    
    # Convert the dictionary response to DocumentKeywords model
    return DocumentKeywords.model_validate(resp_dict)

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test code
    test_md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"
    test_doc_title = "Front and Rear Seat Spacing Definition"
    test_content = "Test content for keyword generation..."
    
    result = make_doc_keywords(test_md_info_path, test_doc_title, test_content)
    print(f"Generated keywords: {result.model_dump(indent=2)}") 