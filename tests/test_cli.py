"""Tests for the ``extract_cli.py`` CLI entry point.

Uses ``--provider mock`` so the whole run is offline and deterministic —
no network call, no API key.
"""

from __future__ import annotations

import json

import pytest

from extract_cli import main


def test_mock_provider_prints_valid_ticket_json(capsys):
    rc = main(["--provider", "mock", "My order #123 never arrived!"])
    assert rc == 0
    out = capsys.readouterr().out
    ticket = json.loads(out)
    assert ticket["category"] == "shipping"
    assert ticket["requires_human"] is True


def test_no_input_text_is_an_error(capsys, monkeypatch):
    # Simulate an empty stdin (no positional text, no --input file).
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(""))
    rc = main(["--provider", "mock"])
    assert rc == 2
    assert "No input text" in capsys.readouterr().err


def test_input_file_is_read(tmp_path, capsys):
    ticket_file = tmp_path / "ticket.txt"
    ticket_file.write_text("Double charged on invoice #42, please refund.")
    rc = main(["--provider", "mock", "--input", str(ticket_file)])
    assert rc == 0
    ticket = json.loads(capsys.readouterr().out)
    assert ticket["category"] == "shipping"


def test_unknown_provider_rejected_by_argparse():
    with pytest.raises(SystemExit) as exc:
        main(["--provider", "not-a-provider", "hello"])
    assert exc.value.code == 2
