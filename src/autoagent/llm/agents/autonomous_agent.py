# autoagent/llm/agents/autonomous_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class AutonomousAgent(BaseAgent):
    """
    AutoGPT–style: plan → execute → evaluate → re-plan in a loop.
    """

    def __init__(self, config: dict, tool_registry: dict, max_iters: int = 5):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )
        self.max_iters = max_iters

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        memory = []
        goal = input_text

        for i in range(self.max_iters):
            prompt = f"Goal: {goal}\nMemory:\n{memory}\nNext action?"
            resp = self.llm.chat([{"role": "user", "content": prompt}])
            trace.append({f"step_{i+1}": resp})
            memory.append(resp)

        return {"answer": memory[-1] if memory else "", "trace": trace}
