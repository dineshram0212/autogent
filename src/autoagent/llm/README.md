# `autoagent/llm` Module Usage Guide

This README shows **step‐by‐step** how to wire up and call your LLMs using the modules in the **`agentlib/llm/`** folder. You’ll see how **client.py**, **resolver.py**, **prompts.py**, **factory.py**, and the **agent classes** work together to let you call any LLM in a pluggable, consistent way.

---

## 📦 Module Overview

```
agentlib/llm/
├── client.py        # LLMClient: chat / complete / embed / stream
├── prompts.py       # Prompt templates: ReAct, CoT, etc.
├── resolver.py      # resolve_llm_config → merges Base/Tenant/User
├── factory.py       # AgentFactory: map “react”/“rag”/… → Agent class
└── agents/
    ├── base_agent.py        # BaseAgent interface
    ├── react_agent.py       # ReActAgent
    ├── rag_agent.py         # RAGAgent
    ├── cot_agent.py         # CoTAgent
    ├── tot_agent.py         # TOTAgent
    ├── self_refine_agent.py # SelfRefineAgent
    ├── code_agent.py        # CodeAgent
    ├── autonomous_agent.py  # AutonomousAgent
    └── convo_overlap_agent.py  # ConvoOverlapAgent
```

---

## 1. Resolve Your LLM Configuration

Your **three-tier config** (Founder → Tenant → User) lives in `config/`.  At runtime you merge them:

```python
from agentlib.config.base_config import BaseConfig
from agentlib.config.tenant_config import TenantConfig
from agentlib.config.user_config import UserConfig
from agentlib.llm.resolver import resolve_llm_config

base_cfg   = BaseConfig(api_key="encrypted-founder-key")
tenant_cfg = TenantConfig(llm_enabled=True, encrypted_api_key="encrypted-tenant-key")
user_cfg   = UserConfig(use_llm=False)

# This returns: {"api_key": "...", "model": "...", "base_url": "...", "source": "..."}
llm_conf = resolve_llm_config(base_cfg, tenant_cfg, user_cfg)
```

---

## 2. Instantiate the LLM Client

Use `LLMClient` to call chat, complete, embed, or stream:

```python
from agentlib.llm.client import LLMClient

client = LLMClient(
    api_key=llm_conf["api_key"],
    model=llm_conf["model"],
    base_url=llm_conf.get("base_url")
)

# Simple chat
reply = client.chat([
    {"role":"system","content":"You are a helpful assistant."},
    {"role":"user","content":"Hello!"}
])
print(reply)

# Streaming
for chunk in client.chat(messages, stream=True):
    print(chunk, end="", flush=True)
```

---

## 3. Use Prompt Templates

Grab and format the system prompt for ReAct or other patterns:

```python
from agentlib.llm.prompts import REACT_PROMPT_TEMPLATE

prompt = REACT_PROMPT_TEMPLATE.format(
    tool_names="search, calculator",
    query="What is the capital of France?"
)
```

---

## 4. Build & Run an Agent via Factory

You don’t import agents directly—use `AgentFactory` to get the right class by name:

```python
from agentlib.llm.factory import AgentFactory
from agentlib.tools.registry import TOOL_REGISTRY

# e.g. agent_type = "react", "rag", "cot", etc.
agent_type = "react"
agent = AgentFactory.get(agent_type, llm_conf, TOOL_REGISTRY)

# Run a query
result = agent.run("Search for Python frameworks and summarize", context=[])
print("Answer:", result["answer"])
for step in result["trace"]:
    print(step)
```

---

## 5. Direct Agent Instantiation (Optional)

If you need fine control, you can also:

```python
from agentlib.llm.agents.react_agent import ReActAgent

react_agent = ReActAgent(llm_conf, TOOL_REGISTRY, max_steps=4)
output = react_agent.run("Calculate 2+2 and then search for its history", context=[])
```

---

## 6. Adding a New Agent

1. **Create** `agents/my_agent.py`, subclass `BaseAgent` and implement `.run(...)`.  
2. **Register** it in `factory.py`:

   ```python
   from .agents.my_agent import MyAgent
   AGENT_MAP["my_pattern"] = MyAgent
   ```

3. **Use** it via `AgentFactory.get("my_pattern", llm_conf, TOOL_REGISTRY)`.

---

## 7. Summary

- **`client.py`**: your single glue to talk to any LLM provider  
- **`resolver.py`**: merges configs to decide keys/models at runtime  
- **`prompts.py`**: store & maintain all your agent prompt templates  
- **`factory.py`**: hide direct imports—get agents by name  
- **`agents/`**: mix-and-match patterns (ReAct, RAG, CoT, etc.)  

With this structure you can **plug in** new models, new agent behaviors, and new prompt patterns without touching existing code—just update config or drop in a new module. Enjoy building!  
```