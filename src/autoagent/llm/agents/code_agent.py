# autoagent/llm/agents/code_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class CodeAgent(BaseAgent):
    """
    Generates code and (optionally) loops on execution errors.
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
        # 1) Prompt for code
        prompt = f"Write Python code for the following:\n{input_text}"
        code = self.llm.chat([{"role": "user", "content": prompt}])
        trace.append({"generated_code": code})

        # 2) (Optional) execute in sandbox & capture errors/results
        #    For now we return code only
        return {"answer": code, "trace": trace}
