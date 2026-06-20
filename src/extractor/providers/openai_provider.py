"""OpenAI provider — uses the official `openai` SDK (chat completions)."""

from __future__ import annotations

from .base import LLMProvider, ProviderError

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise ProviderError(
                "The 'openai' package is required for the OpenAI provider: "
                "pip install openai"
            ) from exc
        self._client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as exc:
            raise ProviderError(f"OpenAI request failed: {exc}") from exc
        return resp.choices[0].message.content or ""
