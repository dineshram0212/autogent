from config.encryption import decrypt_value

class UserConfig:
    def __init__(self, encrypted_config: dict):
        """
        encrypted_config = {
            "api_key": "...",  # encrypted string
            "model_name": "...",  # plain or encrypted
            "base_url": "...",  # plain or encrypted
        }
        """
        self._config = encrypted_config

    def get_api_key(self) -> str:
        return decrypt_value(self._config["api_key"])

    def get_model_name(self) -> str:
        return decrypt_value(self._config.get("model_name", "Z2FwdC00"))

    def get_base_url(self) -> str:
        return decrypt_value(self._config.get("base_url", "aHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MQ=="))
