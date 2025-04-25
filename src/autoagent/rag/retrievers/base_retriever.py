# autoagent/rag/retrievers/base_retriever.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Return a list of {'source': id, 'text': snippet, 'score': float}.
        """
        pass
