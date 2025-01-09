from typing import List
from dotenv import load_dotenv
import rich

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.scored_recovered_section import ScoredRecoveredSection
from mrag_vdb.dto.rag_context import RagContext

def query2sortedsections_reranked(rag_context: RagContext, sections: List[ScoredRecoveredSection]) -> List[ScoredRecoveredSection]:
    """对检索到的文档片段进行重排序"""
    # 初始化日志系统
    setup_logger_handlers()
    
    # 如果没有检索到文档片段，直接返回空列表
    if not sections:
        rich.print("[yellow]No sections to rerank[/yellow]")
        return []
    
    # 按相似度得分排序
    sorted_sections = sorted(sections, key=lambda x: x.score, reverse=True)
    
    # 打印重排序结果
    rich.print(f"[green]Reranked {len(sorted_sections)} sections[/green]")
    
    return sorted_sections
