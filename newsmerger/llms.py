from typing import Protocol, runtime_checkable


class LLMUnavailableError(LookupError):
    """The LLM a plugin asked for is not loaded."""


@runtime_checkable
class LLM(Protocol):
    """Serves language models. Without `model`, each method uses the
    backend's default model for it."""

    def prompt(
        self,
        prompt: str,
        *,
        model: str | None = None,
        json_mode: bool = False,
        context_length: int | None = None,
    ) -> str:
        """The model's response to `prompt`; constrained to JSON with
        `json_mode`. `context_length` sets the context window, in tokens,
        for prompts longer than the backend's default."""
        ...

    def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """One embedding per text, in order."""
        ...


def strip_code_fence(text: str) -> str:
    """`text` without surrounding whitespace and the Markdown code fence some
    models wrap their answer in."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # Remove first line
        text = text.rsplit("```", 1)[0]  # Remove last ```
    return text.strip()
