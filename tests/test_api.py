"""Tests for the FastAPI web backend (``api.py``).

Everything here exercises the offline heuristic path (``provider == "demo"`` or
no ``api_key`` supplied) — never a real LLM call — so the suite stays fast and
network-free, matching the rest of the test suite.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_info_lists_schema_and_providers():
    resp = client.get("/api/info")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["schema"]) == {
        "category", "urgency", "sentiment", "summary", "entities", "requires_human",
    }
    assert "demo" in body["providers"]


def test_extract_rejects_empty_text():
    resp = client.post("/api/extract", json={"text": "   "})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is False
    assert "text" in body["error"].lower()


def test_extract_demo_mode_uses_heuristic():
    resp = client.post("/api/extract", json={
        "text": "My order #123 never arrived and I'm furious, refund me now!",
        "provider": "demo",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["mode"] == "heuristic"
    ticket = body["ticket"]
    assert ticket["category"] == "shipping"
    assert ticket["sentiment"] == "negative"
    assert ticket["urgency"] == "high"
    assert ticket["requires_human"] is True
    assert "order #123" in ticket["entities"] or "#123" in ticket["entities"]


def test_extract_without_api_key_falls_back_to_heuristic():
    # A real provider name with no key must not attempt a network call.
    resp = client.post("/api/extract", json={
        "text": "Thanks so much, love the new update!",
        "provider": "anthropic",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["mode"] == "heuristic"
    assert body["ticket"]["sentiment"] == "positive"
