# autoagent/llm/agents/rag_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class RAGAgent(BaseAgent):
    """
    Retrieval-Augmented Generation: fetches docs, injects into prompt, then calls LLM.
    """

    def __init__(self, config: dict, tool_registry: dict, retriever=None):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )
        self.retriever = retriever  # e.g. an instance of your Retriever

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        # 1) Retrieve relevant context
        docs = self.retriever.retrieve(input_text) if self.retriever else []
        trace.append({"retrieved_docs": docs})

        # 2) Build prompt with docs
        prompt = f"""Use the following context to answer.
        Context:
        {chr(10).join(docs)}

        Question: {input_text}
        """
        # 3) Call LLM
        answer = self.llm.chat([{"role": "user", "content": prompt}])
        trace.append({"llm_answer": answer})

        return {"answer": answer, "trace": trace}
