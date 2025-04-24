from typing import Optional
from config.encryption import decrypt_value


class BaseConfig:
    """Default LLM config set by the superuser (founder). Always active."""
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = "https://api.openai.com/v1"):
        self.api_key = decrypt_value(api_key)
        self.model = model
        self.base_url = base_url

    def get_config(self):
        return {
            "api_key": self.api_key,
            "model": self.model,
            "base_url": self.base_url,
            "source": "base"
        }


class TenantConfig:
    """Tenant-level config set by your business client."""
    def __init__(self, llm_enabled: bool, encrypted_api_key: Optional[str] = None,
                 model: Optional[str] = None, base_url: Optional[str] = None):
        self.llm_enabled = llm_enabled
        self.api_key = decrypt_value(encrypted_api_key) if encrypted_api_key and llm_enabled else None
        self.model = model
        self.base_url = base_url

    def get_config(self, fallback: BaseConfig):
        if not self.llm_enabled:
            return fallback.get_config()
        return {
            "api_key": self.api_key or fallback.api_key,
            "model": self.model or fallback.model,
            "base_url": self.base_url or fallback.base_url,
            "source": "tenant"
        }


class UserConfig:
    """Per-user config, used only if tenant or founder allows it (very rare)."""
    def __init__(self, use_llm: bool, encrypted_api_key: Optional[str] = None,
                 model: Optional[str] = None, base_url: Optional[str] = None):
        self.use_llm = use_llm
        self.api_key = decrypt_value(encrypted_api_key) if encrypted_api_key and use_llm else None
        self.model = model
        self.base_url = base_url

    def get_config(self, tenant_or_fallback_config: dict):
        if not self.use_llm:
            return tenant_or_fallback_config
        return {
            "api_key": self.api_key or tenant_or_fallback_config["api_key"],
            "model": self.model or tenant_or_fallback_config["model"],
            "base_url": self.base_url or tenant_or_fallback_config["base_url"],
            "source": "user"
        }
