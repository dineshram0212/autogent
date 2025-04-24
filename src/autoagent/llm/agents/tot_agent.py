# autoagent/llm/agents/tot_agent.py

from autoagent.llm.client import LLMClient
from .base_agent import BaseAgent

class TOTAgent(BaseAgent):
    """
    Tree-of-Thoughts: explores multiple reasoning branches and picks the best.
    """

    def __init__(self, config: dict, tool_registry: dict, branches: int = 3):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )
        self.branches = branches

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        candidates = []

        # 1) Generate several reasoning paths
        for i in range(self.branches):
            prompt = f"[Path {i+1}] Think step-by-step:\n{input_text}"
            out = self.llm.chat([{"role": "user", "content": prompt}])
            candidates.append(out)
            trace.append({f"path_{i+1}": out})

        # 2) Naïvely pick the first (real logic would score/prune)
        best = candidates[0] if candidates else ""
        return {"answer": best, "trace": trace}
