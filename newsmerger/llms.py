from typing import Protocol, runtime_checkable


class LLMUnavailableError(LookupError):
    """The LLM a plugin asked for is not loaded."""


@runtime_checkable
class LLM(Protocol):
    """Serves language models. Without `model`, each method uses the
    backend's default model for it."""

    def prompt(
        self, prompt: str, *, model: str | None = None, json_mode: bool = False
    ) -> str:
        """The model's response to `prompt`; constrained to JSON with
        `json_mode`."""
        ...

    def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """One embedding per text, in order."""
        ...
