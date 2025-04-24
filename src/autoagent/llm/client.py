import openai
from typing import List, Dict, Any, Optional

class LLMClient:
    """
    Wrapper around OpenAI’s Python SDK for chat, completion, and embeddings.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
        embedding_model: str = "text-embedding-ada-002",
    ):
        openai.api_key = api_key
        if base_url:
            openai.api_base = base_url
        self.model = model
        self.embedding_model = embedding_model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any
    ) -> str:
        """
        messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
        Returns the assistant’s reply text.
        """
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return resp.choices[0].message.content.strip()

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any
    ) -> str:
        """
        Simple text completion (for non-chat use cases).
        """
        resp = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return resp.choices[0].text.strip()

    def embed(self, inputs: List[str]) -> List[List[float]]:
        """
        Returns a list of embedding vectors for the given inputs.
        """
        resp = openai.Embedding.create(
            model=self.embedding_model,
            input=inputs
        )
        # The response data is a list of dicts with "embedding" and "index"
        return [item["embedding"] for item in resp["data"]]
