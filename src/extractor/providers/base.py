"""Provider abstraction.

Every LLM provider is reduced to one capability the extractor needs: given a
system prompt and a user prompt, return the model's text response. This narrow
interface is what lets Anthropic, OpenAI, Gemini, and a test mock be swapped
freely — the JSON parsing, schema validation, and retry logic above it never
need to know which provider produced the text.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """A minimal text-in/text-out LLM interface."""

    name: str = "base"

    @abstractmethod
    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        """Return the model's text completion for ``system`` + ``user``."""
        raise NotImplementedError


class ProviderError(RuntimeError):
    """Raised when a provider call fails (auth, network, bad response)."""
