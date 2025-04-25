# Orchestrator (Executor) Module

This folder provides the **runtime “glue”** that wires together your configs, agents, tools, and conversation state into a working session. It exposes a simple API to:

1. **Start** a new session  
2. **Handle** each incoming user message  
3. **Pause/Resume** for supervisor override  
4. **Route** flows → agents → tools  

---

## 📂 Folder Structure

```
agentlib/orchestrator/
├── session_router.py         # map flow names → Agent class + tools
├── conversation_manager.py   # track full vs LLM‐only histories & pause state
├── supervisor_channel.py     # inject supervisor turns without feeding LLM
└── agent_runner.py           # high‐level session API: start_session, handle_message
```

---

## ⚙️ session_router.py

**Responsibility**  
Given a tenant’s flow definition (agent_type, tool list, params), instantiate the correct Agent with only the tools it needs.

**Key class & method**  
```python
class SessionRouter:
    def __init__(self, tenant_flows: dict, tool_registry: dict): ...
    def get_agent(self, flow_name: str, llm_config: dict) -> BaseAgent: ...
```

- **tenant_flows**: `{ flow_name: { agent_type, tools, agent_params } }`  
- **tool_registry**: global `{ tool_key: ToolClass }`  

Returns an agent ready to call `.run(user_input, context)`.

---

## ⚙️ conversation_manager.py

**Responsibility**  
Keep two parallel logs per session:

- **Full history** (user + assistant + supervisor)  
- **LLM history** (only user + assistant)  

Also tracks a **paused** flag for supervisor takeover.

**Key API**  
```python
mgr = ConversationManager()
mgr.create_session(session_id)
mgr.append_user(session_id, text)
mgr.append_assistant(session_id, text)
mgr.inject_supervisor(session_id, text)
mgr.is_paused(session_id) → bool
mgr.get_llm_history(session_id) → list[{"role","content"}]
mgr.get_full_history(session_id) → list[{"role","content"}]
mgr.pause(session_id); mgr.resume(session_id)
```

---

## ⚙️ supervisor_channel.py

**Responsibility**  
Expose a simple interface (and optional WebSocket) for a human supervisor to **take over** a session:

- **take_over()** → pause the LLM  
- **inject()**   → add supervisor turn to full history only  
- **release()**  → resume the LLM  

```python
class SupervisorChannel:
    def __init__(self, convo_mgr: ConversationManager): ...
    def take_over(self, session_id: str): ...
    def inject(self, session_id: str, content: str): ...
    def release(self, session_id: str): ...
```

---

## ⚙️ agent_runner.py

**Responsibility**  
The single entrypoint for managing sessions end-to-end:

1. **start_session()** — register tenant_cfg, user_cfg, available flows  
2. **handle_message()** —  
   - Check pause state  
   - Append user turn  
   - Resolve LLM config (founder → tenant → user)  
   - Instantiate agent via `SessionRouter`  
   - Call `agent.run()` with `conversation_manager.get_llm_history()`  
   - Append assistant turn  
   - Return `{ answer, trace }`  

```python
class AgentRunner:
    def __init__(self, base_cfg, tool_registry): ...
    def start_session(self, session_id, tenant_cfg, user_cfg, tenant_flows): ...
    def handle_message(self, session_id, user_message, flow_name) -> dict: ...
```

---

## 🚀 Example Usage

```python
from agentlib.config.base_config import BaseConfig
from agentlib.config.tenant_config import TenantConfig
from agentlib.config.user_config import UserConfig
from agentlib.orchestrator.agent_runner import AgentRunner
from agentlib.tools.registry import TOOL_REGISTRY

# 1) Prepare configs
base_cfg   = BaseConfig(api_key="encrypted-founder")
tenant_cfg = TenantConfig(llm_enabled=True, encrypted_api_key="encrypted-tenant")
user_cfg   = UserConfig(use_llm=False)

# 2) Define tenant flows
tenant_flows = {
  "food_ordering": {
    "agent_type": "react",
    "tools": ["menu_db","price_calc","db_writer"],
    "agent_params": {"max_steps":5}
  }
}

# 3) Initialize Runner
runner = AgentRunner(base_cfg, TOOL_REGISTRY)

# 4) Start a session
session_id = "sess_1234"
runner.start_session(session_id, tenant_cfg, user_cfg, tenant_flows)

# 5) Handle messages
resp1 = runner.handle_message(session_id, "Hi, I'd like to order.", "food_ordering")
print(resp1["answer"])

# 6) Supervisor takes over (optional)
from agentlib.orchestrator.supervisor_channel import SupervisorChannel
sup = SupervisorChannel(runner.convo_mgr)
sup.take_over(session_id)
sup.inject(session_id, "We’re out of muffins; please offer scones instead.")
sup.release(session_id)

# 7) Continue conversation
resp2 = runner.handle_message(session_id, "Okay, I'll have the scones then.", "food_ordering")
print(resp2["answer"])
```

---

With these modules you have a **framework‐agnostic**, **pluggable** execution layer that can be embedded in any web service or CLI to power multi‐tenant, human‐augmented LLM agents.