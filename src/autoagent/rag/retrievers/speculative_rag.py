# autoagent/rag/retrievers/speculative_rag.py
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever
from autoagent.llm.client import LLMClient

class SpeculativeRAG(BaseRetriever):
    """
    In parallel: generate multiple query rewrites, retrieve for each,
    then vote/score to pick best passages.
    """
    def __init__(self, api_key: str, llm_model: str, embedder, store, reranker=None, n_queries: int = 3):
        self.llm = LLMClient(api_key, llm_model)
        self.embedder = embedder
        self.store = store
        self.reranker = reranker
        self.n_queries = n_queries

    def _gen_and_retrieve(self, q: str):
        hypo_q = self.llm.chat([{"role":"user","content":f"Rephrase this query: {q}"}])
        emb = self.embedder.embed([hypo_q])[0]
        docs = self.store.query(emb)
        return docs

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        with ThreadPoolExecutor() as ex:
            futures = [ex.submit(self._gen_and_retrieve, query) for _ in range(self.n_queries)]
            all_docs = []
            for f in futures:
                all_docs.extend(f.result())
        # optional rerank
        if self.reranker:
            all_docs = self.reranker.rerank(query, all_docs)
        # dedupe and top_k
        seen, unique = set(), []
        for d in all_docs:
            if d['source'] not in seen:
                unique.append(d); seen.add(d['source'])
            if len(unique) >= top_k: break
        return unique
