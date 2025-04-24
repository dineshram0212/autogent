# autoagent/llm/agents/react_agent.py

import json
from autoagent.llm.client import LLMClient
# from autoagent.llm.prompts import REACT_PROMPT_TEMPLATE
from .base_agent import BaseAgent

REACT_PROMPT_TEMPLATE = ''

class ReActAgent(BaseAgent):
    """
    Implements the ReAct pattern: interleaved reasoning and tool calls.
    """

    def __init__(self, config: dict, tool_registry: dict, max_steps: int = 5):
        super().__init__(config, tool_registry)
        self.llm = LLMClient(
            api_key=config["api_key"],
            model=config["model"],
            base_url=config.get("base_url")
        )
        self.max_steps = max_steps

    def call_tool(self, name: str, arg: str) -> str:
        tool_cls = self.tools.get(name)
        if not tool_cls:
            return f"[ERROR: unknown tool '{name}']"
        return tool_cls().run(arg)

    def run(self, input_text: str, context: str = "") -> dict:
        trace = []
        tools_list = ", ".join(self.tools.keys())
        system = REACT_PROMPT_TEMPLATE.format(
            tool_names=tools_list, query=input_text
        )
        messages = [{"role": "system", "content": system}]

        for step in range(self.max_steps):
            # 1) Ask the LLM
            resp = self.llm.chat(messages)
            trace.append({"step": step + 1, "llm": resp})

            # 2) Parse JSON
            try:
                action = json.loads(resp)
                name = action.get("action")
                if name == "final_answer":
                    return {"answer": action.get("output", ""), "trace": trace}
                arg = action.get("input", "")
            except Exception:
                return {"answer": "[ERROR: invalid JSON from LLM]", "trace": trace}

            # 3) Run tool
            result = self.call_tool(name, arg)
            trace.append({"tool": name, "input": arg, "result": result})

            # 4) Feed observation back
            messages.append({"role": "assistant", "content": resp})
            messages.append({"role": "user", "content": f"Observation: {result}"})

        return {"answer": "[Stopped: max steps reached]", "trace": trace}
