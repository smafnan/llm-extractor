"""A deterministic mock provider for offline tests and demos.

It needs no API key or network. You give it a queue of canned responses (or a
callable), and each ``complete`` call returns the next one. This lets the test
suite exercise the *entire* extraction pipeline — prompt construction, JSON
parsing, repair, schema validation, and retry feedback — without ever calling a
real LLM.
"""

from __future__ import annotations

from collections.abc import Callable

from .base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def __init__(
        self,
        responses: list[str] | Callable[[str, str], str] | None = None,
    ) -> None:
        self._responses = list(responses) if isinstance(responses, list) else None
        self._callable = responses if callable(responses) else None
        self._i = 0
        self.calls: list[tuple[str, str]] = []  # record (system, user) per call

    def complete(self, system: str, user: str, *, max_tokens: int = 1024) -> str:
        self.calls.append((system, user))
        if self._callable is not None:
            return self._callable(system, user)
        if self._responses:
            # Return the next queued response; repeat the last one if exhausted.
            idx = min(self._i, len(self._responses) - 1)
            self._i += 1
            return self._responses[idx]
        return "{}"
