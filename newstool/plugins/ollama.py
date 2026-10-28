"""The `ollama` LLM: one Ollama server, with default models for prompts and
embeddings that processors may override."""

import ollama
import pydantic

from ..llms import LLMType
from . import PluginOptions, PluginTypes, Services

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_CHAT_MODEL = "gemma4:12b"
DEFAULT_EMBED_MODEL = "mxbai-embed-large:latest"


class Options(PluginOptions):
    api_base: str = DEFAULT_OLLAMA_URL
    api_key: pydantic.SecretStr | None = None
    chat_model: str = DEFAULT_CHAT_MODEL
    embed_model: str = DEFAULT_EMBED_MODEL


class OllamaLLM:
    options_model = Options

    def __init__(self, options: Options, services: Services) -> None:
        self.client = ollama_client(options)
        self.chat_model = options.chat_model
        self.embed_model = options.embed_model

    def prompt(
        self,
        prompt: str,
        *,
        model: str | None = None,
        json_mode: bool = False,
        context_length: int | None = None,
    ) -> str:
        # https://gemma4-ai.com/blog/gemma4-json-output
        response = self.client.generate(
            model=model or self.chat_model,
            prompt=prompt,
            stream=False,
            format="json" if json_mode else None,
            options={"num_ctx": context_length} if context_length else None,
        )
        return response.response

    def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        response = self.client.embed(model=model or self.embed_model, input=texts)
        return [list(embedding) for embedding in response.embeddings]


def ollama_client(cfg: Options) -> ollama.Client:
    """An Ollama client, authenticated with a bearer token when one is given."""
    api_key = cfg.api_key.get_secret_value() if cfg.api_key else ""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    return ollama.Client(host=cfg.api_base, headers=headers)


def __newstool_plugin__() -> PluginTypes:
    return [("ollama", LLMType, OllamaLLM)]
