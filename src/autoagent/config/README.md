# Configuration Module (`autoagent/config`)

This folder defines how your AI-agent framework handles configuration across **three hierarchical levels**:

1. **BaseConfig** — default/founder settings (e.g., your OpenAI key)  
2. **TenantConfig** — business-specific overrides (e.g., hospital, hotel, restaurant)  
3. **UserConfig** — per-end-user preferences (optional, typically no LLM access)  
4. **LLM Resolver** — intelligently merges the above to select which key, model, and base URL to use.

---

## 📂 Folder Structure

```
agentlib/config/
├── base_config.py         # Founder-level defaults
├── tenant_config.py       # Client/business-level options
├── user_config.py         # Bottom-level user options (optional)
└── llm_resolver.py        # Merges all three configs into one usable LLM config
```

---

## 1️⃣ `BaseConfig`

```python
from agentlib.config.base_config import BaseConfig

cfg = BaseConfig(
    api_key="encrypted-founder-key",
    model="gpt-4",
    base_url="https://api.openai.com"
)
```

- **Used by default** if tenant/user does not override  
- Typically includes:
  - Encrypted OpenAI/Anthropic key
  - Model/version name
  - Base URL (for custom endpoints)
  - Any org-wide fallback behavior

---

## 2️⃣ `TenantConfig`

```python
from agentlib.config.tenant_config import TenantConfig

cfg = TenantConfig(
    llm_enabled=True,
    encrypted_api_key="encrypted-tenant-key",
    model="gpt-3.5-turbo",
    base_url="https://api.openai.com"
)
```

- Controls whether the tenant is **allowed** to use LLMs  
- Can override:
  - API key
  - Model name
  - Endpoint (Azure/OpenRouter/custom)  
- Meant for business clients (e.g., restaurant chain, hospital)

---

## 3️⃣ `UserConfig`

```python
from agentlib.config.user_config import UserConfig

cfg = UserConfig(
    use_llm=False,  # or True if individual override is needed
    encrypted_api_key=None,  # optional
    model=None,
    base_url=None
)
```

- Rarely used unless per-end-user LLMs are enabled  
- Typically set to `use_llm=False` to **inherit tenant or base config**

---

## 4️⃣ LLM Resolver

This is the **heart of the config logic**.

```python
from agentlib.config.llm_resolver import resolve_llm_config

final_config = resolve_llm_config(base_cfg, tenant_cfg, user_cfg)
# → {
#   "api_key": "decrypted...",
#   "model": "gpt-4",
#   "base_url": "https://api.openai.com",
#   "source": "tenant"  # which level provided the config
# }
```

### Merging Priority:

```text
UserConfig > TenantConfig > BaseConfig
```

- If LLM is disabled at **tenant** or **user** level, `resolve_llm_config` will raise an error  
- If `api_key` is missing, will fallback to base  
- Ensures **only the correct user/tenant** is allowed to access LLMs

---

## 🔐 Security Best Practices

- API keys are stored **encrypted**, using Fernet or another secure layer  
- Decryption occurs only at runtime inside resolver functions  
- Never expose decrypted keys in logs or client-facing code  
- Keys are scoped per tenant and optionally per user  

---

## 🧠 Example Usage in App

```python
# Called inside orchestrator.agent_runner
llm_conf = resolve_llm_config(base_cfg, tenant_cfg, user_cfg)

agent = AgentFactory.get(agent_type, llm_conf, TOOL_REGISTRY)
agent.run("What's on the menu?", context=[])
```

---

## 🔧 Tips for Extension

- Add `plan`, `token_limit`, or `rate_limit` fields to configs for usage control  
- Add `PromptOverrides` or `FlowOverrides` to tenant config for custom prompts  
- Add `plan_features` or tiered config for premium/business tenants  

---

This configuration system allows your framework to **scale across businesses**, while giving each one **safe, isolated, override-able** LLM access that can be managed programmatically or through a UI.
```