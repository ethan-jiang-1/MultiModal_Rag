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

KNOWLEGE_FORMAT = """
<knowledge_section>\n
<source_file>{source_file}</source_file>\n
<knowledge_title>{title}</knowledge_title>\n
<knowledge_content>{content}</knowledge_content>\n
</knowledge_section>\n
"""

def find_collection_names(query: str) -> List[str]:
    return ["papers"]

def query_rewerite(query: str, collection_names: List[str]) -> str:
    return query 

def form_knowledge_sections(scored_sections_reranked:List[ScoredSection]) -> str:
    knowledge_all = ""
    for section in scored_sections_reranked:
        source_file = section.fname_org_doc
        title = section.heading
        content = section.content

        knowledge = KNOWLEGE_FORMAT.format(source_file=source_file,
                                           title=title,
                                           content=content)
        knowledge_all += knowledge
    return knowledge_all

def knowledge_retrieve(query: str, knowledge: str):
    resp = knowlege_gen_by_gpt(query, knowledge)
    return resp

def query2knowledge(query: str, limit: int = 10) -> List[ScoredSection]:
    collection_names = find_collection_names(query)
    query = query_rewerite(query, collection_names)

    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query, limit=limit)

    scored_sections_reranked = query2sortedsections_reranked(query_str, scored_sections_raw)

    knowledge = form_knowledge_sections(scored_sections_reranked)

    resp = knowledge_retrieve(query, knowledge)

    return resp

if __name__ == "__main__":
    setup_logger_handlers()
    
    query_str = "神经网络 中央处理器"
    ret = query2knowledge(query_str)
    rich.print(ret)
    