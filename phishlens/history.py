"""Scan history, kept per visitor in Streamlit's session state.

Each browser session gets its own list. browser_store.py mirrors it to the visitor's localStorage,
so it is restored when they come back. Stored data is untrusted, so merge() validates every row.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from .engine import ScanResult

KEY = "scan_history"
MAX_ROWS = 500
COLUMNS = ["time", "url", "host", "verdict", "p_phishing", "risk", "flags", "reliability", "source"]


def _rows() -> list[dict]:
    if KEY not in st.session_state:
        st.session_state[KEY] = []
    return st.session_state[KEY]


def _bump() -> None:
    st.session_state["hist_version"] = st.session_state.get("hist_version", 0) + 1


def raw_rows() -> list[dict]:
    return list(_rows())


def _clean(r: object) -> dict | None:
    """Validate one row restored from the browser; return None if it is malformed."""
    try:
        if not isinstance(r, dict) or not set(COLUMNS) <= set(r):
            return None
        if r["verdict"] not in ("Phishing", "Legitimate") or r["risk"] not in ("Low", "Moderate", "High", "Critical"):
            return None
        pd.Timestamp(r["time"])
        return {
            "time": str(r["time"]), "url": str(r["url"])[:2000], "host": str(r["host"])[:300],
            "verdict": r["verdict"], "p_phishing": min(max(float(r["p_phishing"]), 0.0), 1.0),
            "risk": r["risk"], "flags": int(r["flags"]),
            "reliability": "Low" if r["reliability"] == "Low" else "Normal",
            "source": "batch" if r["source"] == "batch" else "single",
        }
    except (ValueError, TypeError, KeyError):
        return None


def merge(stored: object) -> bool:
    """Add rows restored from the browser that are not already in the session. True if any were added."""
    if not isinstance(stored, list):
        return False
    rows = _rows()
    seen = {(r["time"], r["url"]) for r in rows}
    new = []
    for item in stored[:MAX_ROWS]:
        c = _clean(item)
        if c and (c["time"], c["url"]) not in seen:
            seen.add((c["time"], c["url"]))
            new.append(c)
    if new:
        rows.extend(new)
        rows.sort(key=lambda r: r["time"])
        del rows[:-MAX_ROWS]
        _bump()
    return bool(new)


def add(result: ScanResult, source: str = "single") -> None:
    rows = _rows()
    rows.append({
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": result.url,
        "host": result.host,
        "verdict": result.verdict,
        "p_phishing": round(result.p_phishing, 4),
        "risk": result.risk,
        "flags": len(result.flags),
        "reliability": result.reliability,
        "source": source,
    })
    del rows[:-MAX_ROWS]
    _bump()


def load() -> pd.DataFrame:
    df = pd.DataFrame(_rows(), columns=COLUMNS)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.iloc[::-1].reset_index(drop=True)  # newest first


def clear() -> None:
    st.session_state[KEY] = []
    _bump()
