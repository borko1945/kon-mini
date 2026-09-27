"""Tests for the opt-in KON_DEBUG_TIMING trace."""

from __future__ import annotations

from pathlib import Path

import pytest

from kon.debug_trace import trace, trace_enabled


def test_trace_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("KON_DEBUG_TIMING", raising=False)
    log_path = tmp_path / "timing.log"

    assert trace_enabled() is False
    trace("request-start")
    trace("request-opened")

    assert not log_path.exists()


def test_trace_appends_label_detail_and_delta(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "timing.log"
    monkeypatch.setenv("KON_DEBUG_TIMING", str(log_path))

    assert trace_enabled() is True
    started_at = trace("request-start", "turn=1")
    trace("request-opened", started_at=started_at)
    trace("first-text", "TextPart", started_at=started_at)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert "request-start turn=1" in lines[0]
    assert "request-opened" in lines[1]
    assert "+" in lines[1] and "ms" in lines[1]
    assert "first-text TextPart" in lines[2]


def test_trace_keeps_working_when_log_path_is_unwritable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("KON_DEBUG_TIMING", str(tmp_path / "missing-dir" / "timing.log"))

    # A broken log path must never break a turn.
    assert trace("request-start") > 0
