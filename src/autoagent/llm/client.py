# autoagent/llm/client.py

import openai
from typing import List, Dict, Any, Iterator, Optional


class LLMClient:
    """
    Wrapper around OpenAI’s Python SDK for chat, completion, embeddings,
    with optional streaming support.
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
        stream: bool = False,
        **kwargs: Any
    ) -> Any:
        """
        messages: [{"role":"system"|"user"|"assistant","content":...}]
        If stream=False (default), returns the full assistant reply as a string.
        If stream=True, returns an iterator of text chunks.
        """
        if stream:
            return self.stream_chat(messages, temperature, max_tokens, **kwargs)
        # non-streaming
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs
        )
        return resp.choices[0].message.content.strip()

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any
    ) -> Iterator[str]:
        """
        Stream the assistant’s reply token-by-token (or chunk-by-chunk).
        Yields each new content delta as it arrives.
        """
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        # Each chunk is a dict with choices: [ { delta: {"role"/"content":...} } ]
        for chunk in resp:
            delta = chunk.choices[0].delta.get("content")
            if delta:
                yield delta

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
        return [item["embedding"] for item in resp["data"]]


'''
Stream Usage Example:
from autoagent.llm.client import LLMClient

client = LLMClient(api_key="sk-…", model="gpt-4")

# Non-stream:
reply = client.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "Hello!"}
])
print(reply)

# Stream:
for chunk in client.chat(
      [
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":"Hello!"}
      ],
      stream=True
    ):
    print(chunk, end="", flush=True)
'''