"""CLI for structured extraction across multiple LLM providers.

You choose the provider and pass its key:

    python extract_cli.py --provider anthropic --api-key sk-ant-... "My order #123 never arrived!"
    python extract_cli.py --provider openai   --api-key sk-...     --input ticket.txt
    python extract_cli.py --provider gemini   --api-key ...        --model gemini-1.5-pro "..."

The API key may also come from the environment so it never lands in shell history:
  ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY, or generic LLM_API_KEY.

Use --provider mock to try the pipeline with no key (returns a canned ticket).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from extractor import (
    AVAILABLE_PROVIDERS,
    ExtractionError,
    ProviderError,
    SupportTicket,
    extract,
    get_provider,
)
from extractor.providers import MockProvider

# Where each provider's key is looked up if --api-key is omitted.
_ENV_KEYS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def _resolve_key(provider: str, cli_key: str | None) -> str | None:
    if cli_key:
        return cli_key
    return os.environ.get(_ENV_KEYS.get(provider, ""), "") or os.environ.get(
        "LLM_API_KEY", ""
    ) or None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Extract a structured support ticket "
                                "from free text using an LLM provider.")
    p.add_argument("text", nargs="?", help="Text to extract from (or use --input).")
    p.add_argument("--provider", default="anthropic", choices=AVAILABLE_PROVIDERS,
                   help="Which LLM provider to use (default: anthropic).")
    p.add_argument("--api-key", default=None,
                   help="Provider API key (else read from env; see --help).")
    p.add_argument("--model", default=None,
                   help="Model id override (else the provider's default).")
    p.add_argument("--input", default=None,
                   help="Read the text from this file instead of the argument.")
    p.add_argument("--max-retries", type=int, default=2)
    args = p.parse_args(argv)

    # Gather input text.
    if args.input:
        text = open(args.input, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("No input text provided.", file=sys.stderr)
        return 2

    # Build the provider.
    try:
        if args.provider == "mock":
            # A canned, schema-valid response so the demo runs with no key.
            provider = MockProvider([json.dumps({
                "category": "shipping", "urgency": "high", "sentiment": "negative",
                "summary": "Customer's order never arrived and wants a refund.",
                "entities": ["order #123"], "requires_human": True,
            })])
        else:
            key = _resolve_key(args.provider, args.api_key)
            provider = get_provider(args.provider, api_key=key, model=args.model)
    except ProviderError as exc:
        print(f"Provider error: {exc}", file=sys.stderr)
        return 2

    # Run the extraction.
    try:
        result = extract(text, SupportTicket, provider, max_retries=args.max_retries)
    except ExtractionError as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 1
    except ProviderError as exc:
        print(f"Provider error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result.data.model_dump(), indent=2))
    print(f"\n# provider={provider.name} attempts={result.attempts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
