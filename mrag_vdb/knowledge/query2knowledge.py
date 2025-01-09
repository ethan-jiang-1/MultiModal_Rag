from typing import List
from dotenv import load_dotenv
import rich

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.dto.rag_answer import RagAnswer
from mrag_vdb.dto.rag_context import RagContext
from mrag_vdb.dto.rag_input import RagInput
from mrag_vdb.knowledge.search_file_refs import search_for_file_refs
from mrag_vdb.knowledge.query_rewrite import query_rewerite
from mrag_vdb.query.query2section_raw import query2section_raw_on_rag_context
from mrag_vdb.rerank.query2section_reranked import query2sortedsections_reranked

def form_knowledge_snippets(sections: List[ScoredRecoveredSection]) -> str:
    """将检索到的文档片段组合成知识片段"""
    # 初始化日志系统
    setup_logger_handlers()
    
    # 如果没有检索到文档片段，返回空字符串
    if not sections:
        rich.print("[yellow]No sections to form knowledge snippets[/yellow]")
        return ""
    
    # 组合知识片段
    knowledge_snippets = "\n\n".join([section.content for section in sections])
    
    # 打印结果
    rich.print(f"[green]Formed knowledge snippets from {len(sections)} sections[/green]")
    
    return knowledge_snippets

def gen_answer_from_knowledge_snippets(query: str, knowledge_snippets: str) -> str:
    """根据知识片段生成答案"""
    # 初始化日志系统
    setup_logger_handlers()
    
    # 如果没有知识片段，返回空字符串
    if not knowledge_snippets:
        rich.print("[yellow]No knowledge snippets to generate answer[/yellow]")
        return ""
    
    # TODO: 实现根据知识片段生成答案的逻辑
    answer = f"Query: {query}\n\nKnowledge snippets:\n{knowledge_snippets}"
    
    # 打印结果
    rich.print("[green]Generated answer from knowledge snippets[/green]")
    
    return answer

def compose_rag_answer(rag_context: RagContext, resp: str, scored_sections_reranked: List[ScoredRecoveredSection]) -> RagAnswer:
    """组合RAG答案"""
    # 初始化日志系统
    setup_logger_handlers()
    
    # 搜索文件引用
    file_refs = search_for_file_refs(resp)
    
    # 创建RAG答案对象
    rag_answer = RagAnswer(
        query=rag_context.get_refined_query(),
        answer=resp,
        file_refs=file_refs,
        scored_sections=scored_sections_reranked
    )
    
    return rag_answer

def query2knowledge(rag_input: RagInput) -> RagAnswer:
    """将查询转换为知识"""
    # 初始化日志系统
    setup_logger_handlers()
    
    # 创建RAG上下文
    rag_context = RagContext(rag_input)
    
    # 重写查询
    query = query_rewerite(rag_context)
    
    # 获取原始文档片段
    scored_sections_raw = query2section_raw_on_rag_context(rag_context)
    
    # 重新排序文档片段
    scored_sections_reranked = query2sortedsections_reranked(rag_context, scored_sections_raw)
    
    # 组合知识片段
    knowledge_snippets = form_knowledge_snippets(scored_sections_reranked)
    
    # 生成答案
    resp = gen_answer_from_knowledge_snippets(query, knowledge_snippets)
    
    # 组合RAG答案
    rag_answer = compose_rag_answer(rag_context, resp, scored_sections_reranked)
    
    return rag_answer

def exam_query2knowledge(query: str, collection_names: List[str], limit_raw: int = 20, limit_rerank: int = 5) -> RagAnswer:
    """用于测试的查询转知识函数"""
    # 创建RAG输入对象
    rag_input = RagInput(
        query=query,
        preferred_kbnames=collection_names,
        limit_raw=limit_raw,
        limit_rerank=limit_rerank
    )
    
    # 调用主函数处理查询
    return query2knowledge(rag_input)

if __name__ == "__main__":
    setup_logger_handlers()
    
    #query_str = "神经网络 中央处理器"
    query_str = "椅背板与旁侧板的保留运动间隙是多少"
    collection_names = ["mrag"]
    rag_answer = exam_query2knowledge(query_str, collection_names)
    rich.print(rag_answer)
    