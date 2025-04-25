# autoagent/tools/base.py

import asyncio
import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from typing import Type, Any, List

logger = logging.getLogger(__name__)

class ToolInput(BaseModel):
    """Base class for tool input definitions."""
    pass

class ToolOutput(BaseModel):
    """Base class for tool output definitions."""
    pass

class BaseTool(ABC):
    """
    Abstract base class for all tools.

    Subclasses define:
      - name: str
      - description: str
      - version: str
      - tags: List[str]
      - categories: List[str]
      - input_model: ToolInput
      - output_model: ToolOutput
      - execute(self, input) -> output
    """
    name: str
    description: str
    version: str = "1.0.0"
    tags: List[str] = []
    categories: List[str] = []
    input_model: Type[ToolInput] = ToolInput
    output_model: Type[ToolOutput] = ToolOutput

    @abstractmethod
    def execute(self, input: ToolInput) -> ToolOutput:
        """Run the tool logic and return a validated output model."""
        ...

    async def async_execute(self, input: ToolInput) -> ToolOutput:
        """Default async wrapper around sync execute."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.execute, input)

    def batch_execute(
        self,
        inputs: List[ToolInput],
        parallel: bool = False,
        timeout: float = None
    ) -> List[ToolOutput]:
        """
        Run multiple inputs through the tool.

        :param parallel: use thread pool
        :param timeout: per-item timeout in seconds
        """
        results: List[ToolOutput] = []
        if parallel:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.execute, inp) for inp in inputs]
                for fut in futures:
                    try:
                        out = fut.result(timeout=timeout)
                    except Exception as e:
                        logger.error("Tool %s batch error: %s", self.name, e)
                        raise
                    results.append(out)
        else:
            for inp in inputs:
                results.append(self.execute(inp))
        return results
