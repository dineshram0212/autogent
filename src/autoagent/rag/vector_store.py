# agentlib/rag/vector_store.py
"""
Vector store abstraction: interface to store and query embeddings.
Includes FAISS and Chroma implementations.
"""

from typing import List, Dict, Any, Optional

class BaseVectorStore:
    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        raise NotImplementedError

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError

class FAISSStore(BaseVectorStore):
    def __init__(self, index=None):
        import faiss
        self.index = index or faiss.IndexFlatL2(768)
        self.metadatas = []

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        import numpy as np
        arr = np.array(embeddings).astype('float32')
        self.index.add(arr)
        self.metadatas.extend(metadatas)

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        import numpy as np
        q = np.array([query_embedding]).astype('float32')
        distances, idxs = self.index.search(q, top_k)
        results = []
        for dist, idx in zip(distances[0], idxs[0]):
            meta = self.metadatas[idx]
            results.append({'metadata': meta, 'score': float(dist)})
        return results

class ChromaStore(BaseVectorStore):
    def __init__(self, client=None, collection_name: Optional[str] = None):
        import chromadb
        self.client = client or chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name or 'default')

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        ids = [str(i) for i in range(len(embeddings))]
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return [{'metadata': m, 'score': s} for m, s in zip(results['metadatas'][0], results['distances'][0])]
