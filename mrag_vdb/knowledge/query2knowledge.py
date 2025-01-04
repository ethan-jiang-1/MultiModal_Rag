from typing import List
from dotenv import load_dotenv
import rich

# 加载环境变量
load_dotenv()

from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection
from mrag_vdb.query.query2section_reranked import query2sortedsections_reranked
from mrag_vdb.utils_llm.llm_knowledge_gen_gpt import knowlege_gen_by_gpt
from mrag_vdb.utils_llm.llm_knowledge_gen_qwen import knowlege_gen_by_qwen
from mrag_vdb.utils_llm.llm_knowledge_gen_ark import knowlege_gen_by_ark
from mrag_vdb.knowledge._knowledge_base import markdown_to_html_with_ids
from mrag_vdb.common.rag_answer import RagAnswer
from mrag_vdb.knowledge.search_file_refs import search_for_file_refs
from mrag_vdb.common.runtime_settings import ModelGptSel

KNOWLEGE_FORMAT = """
<KnowledgeSnippet id="{id}"> n
<Source>{source_file}</Source>\n
<Title>{title}</Title>\n
<Content> {html_content} </Content>\n
</KnowledgeSnippet>\n
"""

# TODO: ethan_pending: how to smart select collections
def find_collection_names(query: str) -> List[str]:
    return ["papers"]

# TODO: ethan_pending: how to smart rewrite...
def query_rewerite(query: str, collection_names: List[str]) -> str:
    return query 

def form_knowledge_snippets(scored_sections_reranked:List[ScoredRecoveredSection]) -> str:
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

def gen_answer_from_knowledge_snippets(query: str, knowledge_snippets: str) -> dict:
    model_gen = ModelGptSel.get_gpt_model()
    if model_gen.startswith("gpt"):
        resp = knowlege_gen_by_gpt(query, knowledge_snippets, model=model_gen)
    elif model_gen.startswith("qwen"):
        resp = knowlege_gen_by_qwen(query, knowledge_snippets, model=model_gen)
    elif model_gen.startswith("ep"):
        resp = knowlege_gen_by_ark(query, knowledge_snippets, model=model_gen)
    else:
        raise ValueError(f"not support model: {model_gen}")
    return resp


def compose_rag_answer(query: str, resp: dict, scored_sections_reranked:List[ScoredRecoveredSection], include_image:bool = True) -> RagAnswer:
    refs_info = search_for_file_refs(query, resp, scored_sections_reranked, include_image=include_image)
    source_names = []
    source_titles = []
    source_pnames = []
    image_names = []
    image_titles = []
    image_pnames = []

    for source_name, src_val in refs_info.items():
        source_pname, source_title = src_val["ref_doc_tuple"]
        source_names.append(source_name)
        source_titles.append(source_title)
        source_pnames.append(source_pname)

        ref_imgs_map = src_val.get("ref_imgs_map", None)
        if isinstance(ref_imgs_map, dict):
            for image_name, img_val in ref_imgs_map.items():
                image_pname, image_title = img_val
                image_names.append(image_name)
                image_titles.append(image_title)
                image_pnames.append(image_pname)

    rag_answer = RagAnswer(answer=resp.get("simple_answer", ""),
                           answer_referenced=resp.get("answer_with_reference", ""),
                           source_names=source_names,
                           source_titles=source_titles,
                           source_pnames=source_pnames,
                           image_names=image_names,
                           image_titles=image_titles,
                           image_pnames=image_pnames)
    return rag_answer

def query2knowledge(query: str, collection_names:List[str], limit: int = 10) -> RagAnswer:
    query = query_rewerite(query, collection_names)

    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query, limit=limit)

    scored_sections_reranked = query2sortedsections_reranked(query, scored_sections_raw)

    knowledge_snippets = form_knowledge_snippets(scored_sections_reranked)

    resp = gen_answer_from_knowledge_snippets(query, knowledge_snippets)

    rag_answer = compose_rag_answer(query, resp, scored_sections_reranked)

    return rag_answer

if __name__ == "__main__":
    setup_logger_handlers()
    
    #query_str = "神经网络 中央处理器"
    query_str = "椅背板与旁侧板的保留运动间隙是多少"
    collection_names = ["mrag"]
    rag_answer = query2knowledge(query_str, collection_names)
    rich.print(rag_answer)
    