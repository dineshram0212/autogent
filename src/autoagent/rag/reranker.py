# autoagent/rag/reranker.py

from typing import List, Dict, Any
from autoagent.llm.client import LLMClient

class Reranker:
    """
    Re-ranks a list of candidate passages using an LLM to score relevance.
    """

    def __init__(self, llm_client: LLMClient):
        """
        :param llm_client: an instance of your LLMClient wrapper
        """
        self.llm = llm_client

    def rerank(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        :param query: original user query
        :param candidates: list of dicts with keys 'source', 'text', and optional 'score'
        :returns: candidates sorted by new 'score' descending
        """
        scored = []
        for cand in candidates:
            prompt = (
                f"On a scale of 0–1, how relevant is the following passage "
                f"to the query: '{query}'?\n\nPassage:\n{cand['text']}"
            )
            # Expect the LLM to return a numeric score as plain text
            resp = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.0)
            try:
                score = float(resp.strip())
            except ValueError:
                score = cand.get('score', 0.0)
            cand['score'] = score
            scored.append(cand)

        # Sort by descending score
        return sorted(scored, key=lambda x: x['score'], reverse=True)
