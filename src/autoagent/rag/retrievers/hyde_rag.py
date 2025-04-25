# autoagent/rag/retrievers/hyde_rag.py
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever
from autoagent.llm.client import LLMClient
from autoagent.rag.embedder import OpenAIEmbedder

class HyDERAG(BaseRetriever):
    """
    HyDE: generate a 'hypothetical answer' via LLM, embed it, then retrieve.
    """
    def __init__(self, api_key: str, llm_model: str, embed_model: str, store):
        self.llm = LLMClient(api_key, llm_model)
        self.embedder = OpenAIEmbedder(api_key, embed_model)
        self.store = store

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1) generate hypothetical answer
        hypo = self.llm.chat([{"role":"user","content":f"Provide a concise answer for: {query}"}])
        # 2) embed hypo
        emb = self.embedder.embed([hypo])[0]
        # 3) retrieve by vector
        return self.store.query(emb, top_k)
