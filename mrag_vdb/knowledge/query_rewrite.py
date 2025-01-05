from dotenv import load_dotenv
#import rich

# 加载环境变量
load_dotenv()

from mrag_vdb.dto.rag_context import RagContext


# TODO: ethan_pending: how to smart select collections
def _find_collection_names(rag_context: RagContext) -> RagContext:
    rag_context.preferred_kbnames = rag_context.input.preferred_kbnames
    return rag_context

# TODO: ethan_pending: how to smart rewrite...
def query_rewerite(rag_context: RagContext) -> RagContext:
    rag_context.refined_query = rag_context.input.query 
    return rag_context
