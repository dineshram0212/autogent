# autoagent/rag/retrievers/hybrid_rag.py
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever
from autoagent.rag.reranker import Reranker

class HybridRAG(BaseRetriever):
    """
    Combines keyword search (provided by text_store) with vector search,
    then optionally reranks.
    """
    def __init__(self, text_store, vector_retriever: BaseRetriever, reranker: Reranker = None):
        self.text_store = text_store
        self.vector_retriever = vector_retriever
        self.reranker = reranker

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1) keyword
        kw_docs = self.text_store.keyword_search(query, top_k)
        # 2) vector
        vec_docs = self.vector_retriever.retrieve(query, top_k)
        combined = kw_docs + vec_docs
        if self.reranker:
            combined = self.reranker.rerank(query, combined)
        # dedupe by source
        seen = set(); unique = []
        for d in combined:
            if d['source'] not in seen:
                seen.add(d['source']); unique.append(d)
            if len(unique) >= top_k: break
        return unique
