import ollama

DEFAULT_OLLAMA_URL = "http://localhost:11434"


def ollama_client(
    api_base: str = DEFAULT_OLLAMA_URL, api_key: str | None = None
) -> ollama.Client:
    """An Ollama client, authenticated with a bearer token when one is given."""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    return ollama.Client(host=api_base, headers=headers)
