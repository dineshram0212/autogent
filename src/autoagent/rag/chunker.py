# autoagent/rag/chunker.py

from typing import List
import re

class Chunker:
    """
    Splits raw text into manageable chunks for indexing & retrieval.
    Supports sentence-based and sliding-window chunking.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 128):
        """
        :param chunk_size: max characters (or tokens) per chunk
        :param overlap: characters (or tokens) to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text on sentence boundaries.
        """
        sentences = re.split(r'(?<=[.!?]) +', text)
        return [s.strip() for s in sentences if s.strip()]

    def sliding_window(self, text: str) -> List[str]:
        """
        Slide a fixed-size window with overlap over the text.
        """
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + self.chunk_size, length)
            chunks.append(text[start:end])
            start += self.chunk_size - self.overlap
        return chunks

    def chunk(self, text: str, mode: str = 'sliding_window') -> List[str]:
        """
        General entrypoint: choose 'sentence' or 'sliding_window'.
        """
        if mode == 'sentence':
            return self.split_by_sentences(text)
        elif mode == 'sliding_window':
            return self.sliding_window(text)
        else:
            raise ValueError(f"Unknown chunking mode: {mode}")
