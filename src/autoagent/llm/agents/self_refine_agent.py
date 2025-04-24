# autoagent/llm/agents/self_refine_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class SelfRefineAgent(BaseAgent):
    """
    Draft → Critique → Refine loop for improved outputs.
    """

    def __init__(self, config: dict, tool_registry: dict, iterations: int = 3):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )
        self.iterations = iterations

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        # 1) Initial draft
        draft = self.llm.chat([{"role": "user", "content": input_text}])
        trace.append({"draft": draft})

        # 2) Iterative critique & refine
        for i in range(self.iterations):
            critique_prompt = f"Critique the following answer:\n{draft}"
            critique = self.llm.chat([{"role": "user", "content": critique_prompt}])
            trace.append({"critique": critique})

            refine_prompt = f"Refine your previous answer based on this critique:\nCritique: {critique}\nAnswer:\n{draft}"
            draft = self.llm.chat([{"role": "user", "content": refine_prompt}])
            trace.append({f"refined_{i+1}": draft})

        return {"answer": draft, "trace": trace}
