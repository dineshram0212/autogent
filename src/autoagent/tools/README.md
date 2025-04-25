# Tools Module

The `autoagent/tools/` folder implements a **pluggable, schema-driven** toolkit pipeline for your agents. Tools encapsulate external actions (DB lookups, API calls, computations) behind well-defined Pydantic schemas, with built-in support for:

- **Registration & Discovery**  
- **Structured I/O** via `ToolInput` / `ToolOutput`  
- **Sync** and **Async** execution  
- **Timeouts**, **Batching**, and **Circuit-Breaker**  
- **Versioning**, **Tags**, and **Categories**  
- **ACL Hooks**, **Logging**, and **Metrics**  
- **Plugin Entry-Points** (setuptools)  

---

## 📂 Folder Structure

```
autoagent/tools/
├── __init__.py             # auto-import builtin tools + expose registry & runner
├── base.py                 # BaseTool, ToolInput, ToolOutput definitions
├── registry.py             # @register_tool + plugin discovery
├── tool_runner.py          # run_tool & run_tool_async with timeouts & logging
└── builtin_tools/          # Drop-in tools (auto-registered on import)
    └── menu_lookup.py      # Example built-in tool
```

---

## 🔑 Key Components

### `base.py`

- **`BaseTool`**  
  Abstract class; define:  
  ```python
  name: str
  description: str
  version: str
  tags: List[str]
  categories: List[str]
  input_model: ToolInput
  output_model: ToolOutput
  ```
- **`ToolInput` / `ToolOutput`**  
  Pydantic models for strict input/output validation.
- **`async_execute` / `batch_execute`**  
  Async wrapper and batch/parallel helpers.

### `registry.py`

- **`tool_registry: Dict[str, BaseTool]`**  
  Global mapping of tool names to classes.
- **`@register_tool`**  
  Decorator to register a custom or built-in tool.
- **Plugin Discovery**  
  Finds external tools via the `autoagent_tools` setuptools entry-point.

### `tool_runner.py`

- **`run_tool(tool_name, input_data, timeout, tenant_id)`**  
  Synchronous execution with:  
  - **ACL checks**  
  - **Pydantic validation**  
  - **Timeout** & **circuit-breaker**  
  - **Logging** (execution time, success/failure)  
- **`run_tool_async(...)`**  
  Async version with `async_execute` and `asyncio.wait_for`.

### `builtin_tools/`

Drop any `.py` here with `@register_tool` and it’s auto-imported:

```python
@register_tool
class MenuLookupTool(BaseTool):
    name = "menu_lookup"
    description = "Lookup menu item"
    version = "1.1.0"
    tags = ["menu","price"]
    categories = ["food_ordering"]

    class Input(ToolInput):
        restaurant_id: str
        item_name: str

    class Output(ToolOutput):
        item_name: str
        price: float
        available: bool

    def execute(self, inp: Input) -> Output:
        # real DB/API logic here
        return Output(item_name=inp.item_name, price=9.99, available=True)
```

---

## 🚀 Usage Examples

### Synchronous Call

```python
from autoagent.tools.tool_runner import run_tool

result = run_tool(
    "menu_lookup",
    {"restaurant_id":"r1","item_name":"Latte"},
    timeout=2.0,
    tenant_id="tenant_123"
)
# -> {'item_name':'Latte','price':9.99,'available':True}
```

### Asynchronous Call

```python
import asyncio
from autoagent.tools.tool_runner import run_tool_async

async def demo():
    out = await run_tool_async(
        "menu_lookup",
        {"restaurant_id":"r1","item_name":"Espresso"},
        timeout=2.0,
        tenant_id="tenant_123"
    )
    print(out)

asyncio.run(demo())
```

### Batch Execution

```python
from autoagent.tools.base import ToolInput
from autoagent.tools.registry import tool_registry

tool_cls = tool_registry["menu_lookup"]
tool = tool_cls()
inputs = [tool.input_model(restaurant_id="r1", item_name=i) for i in ["Latte","Mocha"]]
outputs = tool.batch_execute(inputs, parallel=True, timeout=3.0)
```

---

## 🔧 Extensibility & Improvements

- **Add Custom Tools**: create a new class in `builtin_tools/` or external package, decorate with `@register_tool`.  
- **Support New ACL Logic**: override the `acl_check` function.  
- **Extend Plugin Discovery**: publish tools in PyPI under the `autoagent_tools` entry-point.  
- **Integrate Metrics**: hook into your monitoring system in `tool_runner.py` logs.  
- **Add Circuit Breakers**: customize exception handling and fallback in `run_tool`.

With this setup, any new tool—built-in or third-party—drops straight into your pipeline, and your agents can call them reliably, securely, and with full observability. 