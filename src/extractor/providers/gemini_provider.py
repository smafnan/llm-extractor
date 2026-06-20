"""Google Gemini provider — uses the `google-generativeai` SDK."""

from __future__ import annotations

from .base import LLMProvider, ProviderError

DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL) -> None:
        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover
            raise ProviderError(
                "The 'google-generativeai' package is required for the Gemini "
                "provider: pip install google-generativeai"
            ) from exc
        genai.configure(api_key=api_key)
        self._genai = genai
        self.model = model

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        try:
            model = self._genai.GenerativeModel(
                self.model, system_instruction=system
            )
            resp = model.generate_content(
                user,
                generation_config={"max_output_tokens": max_tokens},
            )
        except Exception as exc:
            raise ProviderError(f"Gemini request failed: {exc}") from exc
        return resp.text or ""
