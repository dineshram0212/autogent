# autoagent/tools/tool_runner.py

import time
import asyncio
import logging
from typing import Any, Dict
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pydantic import ValidationError

from .registry import tool_registry
from .base import ToolInput, ToolOutput, BaseTool

logger = logging.getLogger(__name__)

# Simple ACL hook (override in your app)
def acl_check(tool: BaseTool, tenant_id: str = None) -> bool:
    # Example: deny if tenant_id not allowed
    return True


def run_tool(
    tool_name: str,
    input_data: Dict[str, Any],
    timeout: float = None,
    tenant_id: str = None
) -> Dict[str, Any]:
    """
    Lookup and execute a registered tool with schema validation,
    timeout, ACL check, and logging/metrics.
    """
    tool_cls = tool_registry.get(tool_name)
    if not tool_cls:
        raise ValueError(f"Tool '{tool_name}' not found.")

    tool: BaseTool = tool_cls()
    if not acl_check(tool, tenant_id):
        raise PermissionError(f"Tenant '{tenant_id}' not allowed to use {tool_name}.")

    start_ts = time.time()
    # Validate input
    try:
        parsed_input: ToolInput = tool.input_model.parse_obj(input_data)
    except ValidationError as ve:
        logger.error("Input validation failed for %s: %s", tool_name, ve)
        raise

    # Execute with optional timeout
    try:
        if timeout:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(tool.execute, parsed_input)
                raw_output: ToolOutput = future.result(timeout=timeout)
        else:
            raw_output = tool.execute(parsed_input)
    except TimeoutError:
        logger.error("Tool %s timed out after %ss", tool_name, timeout)
        raise TimeoutError(f"Tool '{tool_name}' execution timed out.")
    except Exception as exc:
        logger.exception("Tool %s execution failed: %s", tool_name, exc)
        raise

    duration = time.time() - start_ts
    logger.info(
        "Tool %s v%s executed in %.3fs (input_size=%d bytes)",
        tool.name, getattr(tool, "version", "?"), duration,
        len(str(input_data).encode('utf-8'))
    )

    return raw_output.dict()


async def run_tool_async(
    tool_name: str,
    input_data: Dict[str, Any],
    timeout: float = None,
    tenant_id: str = None
) -> Dict[str, Any]:
    """
    Async version of run_tool using tool.async_execute.
    """
    tool_cls = tool_registry.get(tool_name)
    if not tool_cls:
        raise ValueError(f"Tool '{tool_name}' not found.")

    tool: BaseTool = tool_cls()
    if not acl_check(tool, tenant_id):
        raise PermissionError(f"Tenant '{tenant_id}' not allowed to use {tool_name}.")

    start_ts = time.time()
    parsed_input = tool.input_model.parse_obj(input_data)

    # Async execute with timeout
    try:
        coro = tool.async_execute(parsed_input)
        if timeout:
            raw_output: ToolOutput = await asyncio.wait_for(coro, timeout)
        else:
            raw_output: ToolOutput = await coro
    except asyncio.TimeoutError:
        logger.error("Tool %s async timed out after %ss", tool_name, timeout)
        raise TimeoutError(f"Tool '{tool_name}' async execution timed out.")
    except Exception as exc:
        logger.exception("Tool %s async execution failed: %s", tool_name, exc)
        raise

    duration = time.time() - start_ts
    logger.info(
        "Tool %s v%s async executed in %.3fs (input_size=%d bytes)",
        tool.name, getattr(tool, "version", "?"), duration,
        len(str(input_data).encode('utf-8'))
    )

    return raw_output.dict()
