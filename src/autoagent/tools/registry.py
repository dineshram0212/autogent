# autoagent/tools/registry.py

import pkg_resources
from typing import Dict, Type
from .base import BaseTool

# Global registry mapping tool names → tool classes
tool_registry: Dict[str, Type[BaseTool]] = {}

def register_tool(tool_cls: Type[BaseTool]) -> Type[BaseTool]:
    """
    Decorator to register a tool class in the global registry.
    Reads name, version, tags, categories from class attributes.
    """
    name = getattr(tool_cls, "name", None)
    if not name:
        raise ValueError("Tool class must have a `name` attribute.")
    tool_registry[name] = tool_cls
    return tool_cls

# Plugin discovery via setuptools entry‐point 'autoagent_tools'
for ep in pkg_resources.iter_entry_points('autoagent_tools'):
    plugin = ep.load()
    if isinstance(plugin, type) and issubclass(plugin, BaseTool):
        register_tool(plugin)
