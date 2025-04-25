# autoagent/rag/retrievers/query_based_rag.py
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever
from autoagent.llm.client import LLMClient

class QueryBasedRAG(BaseRetriever):
    """
    LLM generates refined sub-queries (e.g. split into facets),
    retrieves each, then aggregates.
    """
    def __init__(self, api_key: str, llm_model: str, retriever: BaseRetriever):
        self.llm = LLMClient(api_key, llm_model)
        self.retriever = retriever

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1) ask LLM for sub-queries
        prompt = f"Break this into 3 specific search queries: {query}"
        subqs = self.llm.chat([{"role":"user","content":prompt}]).split('\n')
        results = []
        for sq in subqs:
            docs = self.retriever.retrieve(sq, top_k)
            results.extend(docs)
        # dedupe + top_k
        seen, unique = set(), []
        for d in results:
            if d['source'] not in seen:
                unique.append(d); seen.add(d['source'])
            if len(unique) >= top_k: break
        return unique
