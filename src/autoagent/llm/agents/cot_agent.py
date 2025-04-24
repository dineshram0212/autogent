# autoagent/llm/agents/cot_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class CoTAgent(BaseAgent):
    """
    Chain-of-Thought: prompts the model to think step-by-step without tools.
    """

    def __init__(self, config: dict, tool_registry: dict):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        # 1) Add CoT directive
        prompt = f"Please solve step-by-step:\n{input_text}"
        trace.append({"prompt": prompt})

        # 2) LLM call
        answer = self.llm.chat([{"role": "user", "content": prompt}])
        trace.append({"llm_answer": answer})

        return {"answer": answer, "trace": trace}
