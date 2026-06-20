"""Provider registry — construct a provider by name + API key.

Usage:
    provider = get_provider("anthropic", api_key="sk-...", model="claude-opus-4-8")

Adding a provider is a one-line entry in ``_BUILDERS`` plus its module.
"""

from __future__ import annotations

from .base import LLMProvider, ProviderError
from .mock_provider import MockProvider

# Map provider name -> (module path, class name). Imported lazily so installing
# one provider's SDK is enough; you don't need all of them.
_PROVIDERS = {
    "anthropic": ("anthropic_provider", "AnthropicProvider"),
    "openai": ("openai_provider", "OpenAIProvider"),
    "gemini": ("gemini_provider", "GeminiProvider"),
}

AVAILABLE_PROVIDERS = (*_PROVIDERS.keys(), "mock")


def get_provider(
    name: str, api_key: str | None = None, model: str | None = None
) -> LLMProvider:
    """Instantiate a provider by name.

    ``mock`` needs no key. Real providers require ``api_key``.
    """
    key = name.lower().strip()
    if key == "mock":
        return MockProvider()
    if key not in _PROVIDERS:
        raise ProviderError(
            f"Unknown provider '{name}'. Available: {', '.join(AVAILABLE_PROVIDERS)}"
        )
    if not api_key:
        raise ProviderError(f"Provider '{name}' requires an API key.")

    module_name, class_name = _PROVIDERS[key]
    import importlib
    module = importlib.import_module(f".{module_name}", __package__)
    cls = getattr(module, class_name)
    # Pass model only if the caller specified one (else the provider's default).
    return cls(api_key=api_key, model=model) if model else cls(api_key=api_key)


__all__ = ["LLMProvider", "ProviderError", "MockProvider",
           "get_provider", "AVAILABLE_PROVIDERS"]
