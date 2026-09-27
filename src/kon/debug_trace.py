"""Opt-in timing traces for diagnosing where a turn spends its time.

Set `KON_DEBUG_TIMING` to a file path and Kon appends one line per phase of a
request. The phases are ordered so harness overhead (prompt build, UI dispatch),
connection setup, and the model's own time-to-first-token can be told apart:

    prompt-submitted   - the user hit enter
    agent-run-start    - the agent worker actually started
    request-start      - messages/tools are built, the HTTP request is next
    request-opened     - response headers arrived (DNS + TCP + TLS + queueing)
    first-chunk        - first streamed part of any kind
    first-think        - first reasoning delta (model is thinking, not answering)
    first-text         - first answer text
    first-visible      - the UI rendered the first delta
"""

from __future__ import annotations

import os
import time
from datetime import datetime

_ENV_VAR = "KON_DEBUG_TIMING"


def trace_enabled() -> bool:
    return bool(os.environ.get(_ENV_VAR))


def trace(label: str, detail: str = "", *, started_at: float | None = None) -> float:
    """Append one timing line and return the monotonic timestamp used for it.

    Pass the returned value back as `started_at` to log a delta. When tracing is
    off this is just a clock read, and the log file is never touched.
    """
    now = time.perf_counter()
    if not trace_enabled():
        return now

    delta = f"+{(now - started_at) * 1000:7.1f}ms" if started_at is not None else " " * 11
    line = f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {delta} {label}"
    if detail:
        line += f" {detail}"

    try:
        with open(os.environ[_ENV_VAR], "a", encoding="utf-8") as f:
            f.write(f"{line}\n")
    except OSError:
        pass
    return now
