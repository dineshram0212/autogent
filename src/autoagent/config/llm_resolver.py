from autoagent.config.llm_config import BaseConfig
from autoagent.config.llm_config import TenantConfig
from autoagent.config.llm_config import UserConfig

def resolve_llm_config(
    base_cfg: BaseConfig,
    tenant_cfg: TenantConfig,
    user_cfg: UserConfig
) -> dict:
    """
    Merge in order:
      1. base_cfg (founder defaults)
      2. tenant_cfg (if enabled)
      3. user_cfg   (if enabled)
    Returns a dict: {api_key, model, base_url, source}.
    """
    # 1) founder defaults
    cfg = base_cfg.get_config()

    # 2) tenant override
    cfg = tenant_cfg.get_config(base_cfg)

    # 3) user override
    cfg = user_cfg.get_config(cfg)

    return cfg
