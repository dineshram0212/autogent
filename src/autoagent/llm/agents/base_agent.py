from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Common interface for all agents.
    """

    def __init__(self, config: dict, tool_registry: dict):
        self.config = config
        self.tools = tool_registry

    @abstractmethod
    def run(self, input_text: str, context: str = "") -> dict:
        """
        Execute the agent’s logic.
        Returns dict with keys 'answer', 'trace', and optionally 'tools'.
        """
        pass
