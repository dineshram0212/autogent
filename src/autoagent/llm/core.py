import openai
import configparser
import os

# Load configuration from the config file
def load_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.ini')
    config.read(config_path)
    return config

# Initialize OpenAI API client
def initialize_openai_client():
    config = load_config()

    # Retrieve settings from the config file
    api_key = config.get('OpenAI', 'API_KEY', fallback=None)
    base_url = config.get('OpenAI', 'BASE_URL', fallback=None)
    model_name = config.get('OpenAI', 'MODEL_NAME', fallback='gpt-4')

    if not api_key:
        raise ValueError("API_KEY is missing in the configuration file.")

    # Set OpenAI API key and base URL
    openai.api_key = api_key
    if base_url:
        openai.api_base = base_url

    return model_name

# Function to query the LLM
def query_llm(prompt, **kwargs):
    model_name = initialize_openai_client()
    response = openai.Completion.create(
        model=model_name,
        prompt=prompt,
        **kwargs
    )
    return response