

from typing import List, Optional
from pydantic import Field, PrivateAttr
import os
import dashscope 

from llama_index.core.schema import NodeWithScore
from llama_index.core import QueryBundle
from llama_index.core.postprocessor.node import BaseNodePostprocessor
from llama_index.core.callbacks import CBEventType, EventPayload
from llama_index.core.schema import MetadataMode
from llama_index.core.instrumentation.events.rerank import ReRankEndEvent, ReRankStartEvent
import llama_index.core.instrumentation as instrument

dispatcher = instrument.get_dispatcher(__name__)

class DashScopeRerank(BaseNodePostprocessor):
    model: str = Field(description="Dashscope rerank model name.")
    top_n: int = Field(description="Top N nodes to return.")
    _api_key: Optional[str] = PrivateAttr()

    def __init__(
        self,
        top_n: int = 3,
        model: str = "gte-rerank",
        return_documents: bool = False,
        api_key: Optional[str] = None,
    ):
        try:
            api_key = api_key or os.environ["DASHSCOPE_API_KEY"]
        except IndexError:
            raise ValueError(
                "Must pass in dashscope api key or "
                "specify via DASHSCOPE_API_KEY environment variable "
            )

        super().__init__(top_n=top_n, model=model, return_documents=return_documents)
        self._api_key = api_key

    @classmethod
    def class_name(cls) -> str:
        return "DashScopeRerank"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        dispatcher.event(
            ReRankStartEvent(
                model_name=self.model,
                top_n=self.top_n,
                query=query_bundle,
                nodes=nodes,
            )
        )

        if query_bundle is None:
            raise ValueError("Missing query bundle in extra info.")
        if len(nodes) == 0:
            return []

        with self.callback_manager.event(
            CBEventType.RERANKING,
            payload={
                EventPayload.NODES: nodes,
                EventPayload.MODEL_NAME: self.model,
                EventPayload.QUERY_STR: query_bundle.query_str,
                EventPayload.TOP_K: self.top_n,
            },
        ) as event:
            texts = [
                node.node.get_content(metadata_mode=MetadataMode.EMBED)
                for node in nodes
            ]
            results = dashscope.TextReRank.call(
                model=self.model,
                top_n=self.top_n,
                query=query_bundle.query_str,
                documents=texts,
                api_key=self._api_key,
            )
            new_nodes = []
            for result in results.output.results:
                new_node_with_score = NodeWithScore(
                    node=nodes[result.index].node, score=result.relevance_score
                )
                new_nodes.append(new_node_with_score)
            event.on_end(payload={EventPayload.NODES: new_nodes})

        dispatcher.event(
            ReRankEndEvent(
                nodes=new_nodes,
            )
        )
        return new_nodes

if __name__ == "__main__":
    from dotenv import load_dotenv
    import rich
    load_dotenv() 

    api_key = os.getenv("DASHSCOPE_API_KEY")

    from llama_index.core.data_structs import Node
    from llama_index.core.schema import NodeWithScore

    nodes = [
        NodeWithScore(node=Node(text="text1"), score=0.7),
        NodeWithScore(node=Node(text="text2"), score=0.8),
    ]


    dashscope_rerank = DashScopeRerank(top_n=5, api_key=api_key)
    results = dashscope_rerank.postprocess_nodes(nodes, query_str="<user query>")
    for res in results:
        #print("Text: ", res.node.get_content(), "Score: ", res.score)
        rich.print(res)
