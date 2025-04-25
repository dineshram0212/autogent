# autoagent/rag/retrievers/standard_rag.py
from typing import List, Dict, Any
from autoagent.rag.retrievers.base_retriever import BaseRetriever
from autoagent.rag.embedder import OpenAIEmbedder
from autoagent.rag.vector_store import FAISSStore

class StandardRAG(BaseRetriever):
    """Retrieve top-k via embedding similarity."""
    def __init__(self, api_key: str, store: FAISSStore, model: str = 'text-embedding-ada-002'):
        self.embedder = OpenAIEmbedder(api_key, model)
        self.store = store

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        emb = self.embedder.embed([query])[0]
        return self.store.query(emb, top_k=top_k)
