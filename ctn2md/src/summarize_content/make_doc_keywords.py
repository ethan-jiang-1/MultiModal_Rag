"""Document keywords generation implementation"""
from dotenv import load_dotenv
import rich
import os
import json
import hashlib
import logging

load_dotenv()

from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils_llm.llm_summarize_content import summarize_doc_keywords_by_llm
from ctn2md.src.summarize_content.doc_keywords import DocumentKeywords

def _get_cache_path(md_info: MdInfo) -> str:
    """Get path for cache file"""
    return os.path.join(md_info.get_cache_dir(), "doc_keywords_cache.json")

def _calculate_md5(content: str) -> str:
    """Calculate MD5 hash of content"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def make_doc_keywords(md_info: MdInfo, doc_title: str, full_content: str) -> DocumentKeywords:
    """Generate document keywords using LLM analysis

    Args:
        md_info_path (str): Path to markdown info file
        doc_title (str): Document title
        full_content (str): Full document content

    Returns:
        DocumentKeywords: Structured data containing categorized keywords and summary
    """
    # Get model type
    mctl_summarize_model = md_info.get_md_control("mctl_summarize_model", "gpt")
    if mctl_summarize_model == "gpt":
        model = "gpt-4o"
    elif mctl_summarize_model == "qwen":
        model = "qwen-plus"
    elif mctl_summarize_model == "ark":
        model = "ep-20241220101421-4tj5f"
    else:
        raise ValueError(f"not implemented yet for using {mctl_summarize_model} in sumamrize document")
    
    # Calculate content hash
    content_hash = _calculate_md5(full_content)
    cache_path = _get_cache_path(md_info)
    logging.info(f"Checking cache at: {cache_path}")
    logging.info(f"Content hash: {content_hash}")
    
    # Check cache
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            logging.info(f"Cache exists. Comparing - Model: {model} vs {cache_data.get('model')}, "
                        f"Title: {doc_title} vs {cache_data.get('doc_title')}, "
                        f"Hash: {content_hash} vs {cache_data.get('content_hash')}")
            
            if (cache_data.get('model') == model and 
                    cache_data.get('doc_title') == doc_title and 
                    cache_data.get('content_hash') == content_hash):
                # Cache hit
                logging.info("Cache hit! Using cached result")
                rich.print("[green]Using cached result[/green]")
                return DocumentKeywords.model_validate(cache_data['result'])
            else:
                logging.info("Cache miss: Content or parameters changed")
    else:
        logging.info("No cache file found")
    
    # Cache miss, call LLM
    logging.info(f"Calling LLM with model: {model}")
    resp_dict = summarize_doc_keywords_by_llm(doc_title, full_content, model=model)
    rich.print(resp_dict)
    
    # Save to cache
    cache_data = {
        'model': model,
        'doc_title': doc_title,
        'content_hash': content_hash,
        'result': resp_dict
    }
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    logging.info(f"Saving new result to cache: {cache_path}")
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    # Convert the dictionary response to DocumentKeywords model
    return DocumentKeywords.model_validate(resp_dict)

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()
    
    # Test code
    test_md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"
    test_doc_title = "Front and Rear Seat Spacing Definition"
    test_content = "Test content for keyword generation..."
    
    md_info = MdInfo(test_md_info_path)
    result = make_doc_keywords(md_info, test_doc_title, test_content)
    print(f"Generated keywords: {result.model_dump(indent=2)}") 
