"""Anthropic (Claude) provider — uses the official `anthropic` SDK.

The SDK is imported lazily inside ``__init__`` so the package imports fine without
`anthropic` installed (e.g. when only using the OpenAI provider or the mock).
"""

from __future__ import annotations

from .base import LLMProvider, ProviderError

# Default to the latest, most capable Claude model. Override with --model.
DEFAULT_MODEL = "claude-opus-4-8"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on env
            raise ProviderError(
                "The 'anthropic' package is required for the Anthropic provider: "
                "pip install anthropic"
            ) from exc
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        try:
            resp = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:  # surface a uniform error type to the caller
            raise ProviderError(f"Anthropic request failed: {exc}") from exc
        # response.content is a list of blocks; concatenate the text blocks.
        return "".join(b.text for b in resp.content if b.type == "text")
