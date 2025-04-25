# autoagent/rag/retrievers/long_rag.py
from typing import List, Dict, Any
from autoagent.rag.chunker import Chunker
from autoagent.rag.retrievers.standard_rag import StandardRAG

class LongRAG(StandardRAG):
    """
    For very long documents: chunk them, index per chunk, then
    retrieve per-chunk and reassemble.
    """
    def __init__(self, api_key: str, store, chunk_size: int = 1000, overlap: int = 200):
        super().__init__(api_key, store)
        self.chunker = Chunker(chunk_size, overlap)

    def index_document(self, source: str, text: str):
        """
        Break a long text into chunks and add to the vector store.
        """
        chunks = self.chunker.chunk(text, mode='sliding_window')
        embeddings = self.embedder.embed(chunks)
        metas = [{"source": source, "chunk": i, "text": c} for i, c in enumerate(chunks)]
        self.store.add(embeddings, metas)

    # retrieve remains same as parent
