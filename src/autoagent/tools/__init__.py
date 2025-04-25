# autoagent/tools/__init__.py

# Expose key modules
from .base import BaseTool, ToolInput, ToolOutput
from .registry import register_tool, tool_registry
from .tool_runner import run_tool

# Auto-import all builtin tools so they register themselves on import
import pkgutil, importlib, os

def _import_builtin_tools():
    tools_pkg = os.path.join(os.path.dirname(__file__), "builtin_tools")
    for _, module_name, _ in pkgutil.iter_modules([tools_pkg]):
        importlib.import_module(f"{__name__}.builtin_tools.{module_name}")

_import_builtin_tools()
