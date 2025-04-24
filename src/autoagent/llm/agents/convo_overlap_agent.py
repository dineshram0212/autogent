# autoagent/llm/agents/convo_overlap_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class ConvoOverlapAgent(BaseAgent):
    """
    Conversational agent that can accept supervisor injections mid-dialog.
    """

    def __init__(self, config: dict, tool_registry: dict):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )

    def run(self, input_text: str, context: list = None) -> dict:
        """
        context: list of messages with roles ['user','assistant','supervisor']
        """
        trace = []
        messages = context.copy() if context else []
        messages.append({"role": "user", "content": input_text})
        trace.append({"input": input_text, "context_length": len(messages)})

        answer = self.llm.chat(messages)
        trace.append({"assistant": answer})

        return {"answer": answer, "trace": trace}
