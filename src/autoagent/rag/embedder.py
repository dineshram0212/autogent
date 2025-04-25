# autoagent/rag/embedder.py

from typing import List
import openai
from sentence_transformers import SentenceTransformer

class BaseEmbedder:
    """
    Interface for embedding text into vectors.
    """
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("embed() must be implemented by subclasses")

class OpenAIEmbedder(BaseEmbedder):
    """
    Uses OpenAI's Embedding API.
    """
    def __init__(self, api_key: str, model: str = 'text-embedding-ada-002'):
        openai.api_key = api_key
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = openai.Embedding.create(model=self.model, input=texts)
        # resp.data is list of { embedding: [...], index: i }
        return [d['embedding'] for d in resp['data']]

class HFEmbedder(BaseEmbedder):
    """
    Uses a HuggingFace SentenceTransformer model.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # returns a numpy array; convert to list of lists
        return self.model.encode(texts, show_progress_bar=False).tolist()
