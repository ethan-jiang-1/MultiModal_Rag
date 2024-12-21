from typing import List
from dotenv import load_dotenv
import sys
#import logging
import rich

# 加载环境变量
load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from md2vdb.query.recover_section_for_query import ScoredSection
from md2vdb.utils.util_logging import setup_logger_handlers
from md2vdb.query.query2section_raw import query2section_raw_on_multiple_collection
from md2vdb.query.query2section_reranked import query2sortedsections_reranked
from md2vdb.utils_llm.llm_knowledge_gen_gpt import knowlege_gen_by_gpt
from md2vdb.query.md2html_with_ids import markdown_to_html_with_ids

KNOWLEGE_FORMAT = """
<KnowledgeSnippet id="{id}"> n
<Source>{source_file}</Source>\n
<Title>{title}</Title>\n
<Content> {html_content} </Content>\n
</KnowledgeSnippet>\n
"""

def find_collection_names(query: str) -> List[str]:
    return ["papers"]

def query_rewerite(query: str, collection_names: List[str]) -> str:
    return query 

def form_knowledge_sections(scored_sections_reranked:List[ScoredSection]) -> str:
    knowledge_all = ""
    for ndx, section in enumerate(scored_sections_reranked):
        source_file = section.fname_org_doc
        title = section.heading
        content = section.content

        html_content = markdown_to_html_with_ids(content)

        knowledge = KNOWLEGE_FORMAT.format(id=ndx+1,
                                           source_file=source_file,
                                           title=title,
                                           html_content=html_content)
        section.knowledge_snippet = knowledge
        knowledge_all += knowledge + "\n\n"
    return knowledge_all

def knowledge_retrieve(query: str, knowledge: str, scored_sections_reranked:List[ScoredSection]):
    resp = knowlege_gen_by_gpt(query, knowledge, model="gpt-4o")
    return resp

def search_for_ref_images(query: str, resp: dict, scored_sections_reranked:List[ScoredSection]):
    detailed_refernces = resp.get("detailed_references", None)
    if detailed_refernces is not None:
        for ref in detailed_refernces:
            snippet_id = ref.get("snippet_id", None)
            if snippet_id is not None:
                snippet_id = int(snippet_id) - 1
                if snippet_id >= 0 and snippet_id < len(scored_sections_reranked):
                    ref_section = scored_sections_reranked[snippet_id]
                    rich.print(ref_section)
    return resp

def query2knowledge(query: str, limit: int = 10) -> List[ScoredSection]:
    collection_names = find_collection_names(query)
    query = query_rewerite(query, collection_names)

    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query, limit=limit)

    scored_sections_reranked = query2sortedsections_reranked(query, scored_sections_raw)

    knowledge = form_knowledge_sections(scored_sections_reranked)

    resp = knowledge_retrieve(query, knowledge, scored_sections_reranked)

    return resp

if __name__ == "__main__":
    setup_logger_handlers()
    
    query_str = "神经网络 中央处理器"
    ret = query2knowledge(query_str)
    rich.print(ret)
    