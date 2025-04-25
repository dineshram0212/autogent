# autoagent/rag/retrievers/contextual_rag.py
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever

class ContextualRAG(BaseRetriever):
    """
    Incorporates conversation context into retrieval:
    Adds last n user/assistant turns to the query.
    """
    def __init__(self, retriever: BaseRetriever, context_window: int = 3):
        self.retriever = retriever
        self.context_window = context_window

    def retrieve(self, query: str, context: List[Dict[str,str]] = None, top_k: int = 5) -> List[Dict[str,Any]]:
        # flatten last N turns
        ctx = ""
        if context:
            last = context[-self.context_window*2:]  # user+assistant
            ctx = " ".join(m['content'] for m in last)
        final_q = f"{ctx} {query}" if ctx else query
        return self.retriever.retrieve(final_q, top_k)
