"""FastAPI backend for the LLM Extractor web UI.

Turns free text into a validated SupportTicket. With a real provider + key it uses
the actual LLM extraction engine; with no key it falls back to a transparent
heuristic so the playground is interactive offline. Serves the built React UI.

Run:  uvicorn api:app --reload  →  http://localhost:8000
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from extractor import ExtractionError, ProviderError, SupportTicket, extract, get_provider

ROOT = Path(__file__).resolve().parent

# Comma-separated list of allowed origins; defaults to the app's real dev
# origins (Vite dev server + `uvicorn api:app`) so local dev works with no
# env set. Set ALLOWED_ORIGINS to override for other deployments.
_DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:8000"
_allowed_origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app = FastAPI(title="LLM Extractor API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=_allowed_origins, allow_methods=["*"],
                   allow_headers=["*"])

_POS = {"love", "great", "excellent", "amazing", "happy", "perfect", "thanks", "good"}
_NEG = {"hate", "terrible", "awful", "broken", "useless", "angry", "furious",
        "worst", "disappointed", "refund", "never", "bad"}
_URGENT = {"urgent", "asap", "immediately", "critical", "emergency", "now"}
_CATS = {
    "billing": {"refund", "charge", "charged", "bill", "billing", "payment", "invoice", "money"},
    "bug": {"bug", "error", "crash", "broken", "glitch", "freeze"},
    "shipping": {"ship", "shipping", "deliver", "delivery", "arrive", "arrived", "order", "package"},
    "account": {"account", "login", "password", "sign", "access", "locked"},
}


def _heuristic(text: str) -> dict:
    """A transparent rule-based extractor for the no-key demo."""
    low = text.lower()
    words = set(re.findall(r"[a-z']+", low))

    sentiment = "neutral"
    if len(words & _NEG) > len(words & _POS):
        sentiment = "negative"
    elif words & _POS:
        sentiment = "positive"

    urgency = "high" if words & _URGENT else ("low" if "no rush" in low else "medium")

    category = "general"
    best = 0
    for cat, kws in _CATS.items():
        n = len(words & kws)
        if n > best:
            best, category = n, cat

    entities = re.findall(r"#\d+|\border\s+\w*\d+\w*|[\w.]+@[\w.]+", text, flags=re.I)
    summary = re.split(r"(?<=[.!?])\s", text.strip())[0][:140]
    return {
        "category": category, "urgency": urgency, "sentiment": sentiment,
        "summary": summary, "entities": entities[:6],
        "requires_human": urgency in ("high", "critical") or sentiment == "negative",
    }


class ExtractRequest(BaseModel):
    text: str
    provider: str = "demo"
    api_key: str | None = None
    model: str | None = None


@app.get("/api/info")
def info():
    return {"schema": list(SupportTicket.model_json_schema()["properties"].keys()),
            "providers": ["demo", "anthropic", "openai"]}


@app.post("/api/extract")
def extract_endpoint(req: ExtractRequest):
    if not req.text.strip():
        return {"ok": False, "error": "Please enter some text."}
    if req.provider == "demo" or not req.api_key:
        return {"ok": True, "mode": "heuristic", "attempts": 1, "ticket": _heuristic(req.text)}
    try:
        provider = get_provider(req.provider, api_key=req.api_key, model=req.model)
        result = extract(req.text, SupportTicket, provider)
        return {"ok": True, "mode": "llm", "attempts": result.attempts,
                "ticket": result.data.model_dump()}
    except (ProviderError, ExtractionError) as exc:
        return {"ok": False, "error": str(exc)}


_dist = ROOT / "web" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="web")
