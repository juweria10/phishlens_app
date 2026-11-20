"""Keeps scan history in the visitor's own browser (localStorage) so it survives refreshes.

Nothing is sent to a server: the data lives on the visitor's device, which also makes it private
per visitor on a shared deployment. If the browser blocks storage, history falls back to the session.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from . import history

STORE_KEY = "phishlens.history.v1"
_component = components.declare_component("phishlens_store", path=str(Path(__file__).parent / "store_frontend"))


def sync() -> None:
    """Call once at the very end of the script, after the page has rendered."""
    ss = st.session_state
    if ss.get("store_broken"):          # component unavailable on this machine: session-only history
        return
    hydrated = ss.get("hist_hydrated", False)
    version = ss.get("hist_version", 0)

    payload = None
    if hydrated and ss.get("hist_sent") != version:   # only ship data to the browser when it changed
        payload = json.dumps(history.raw_rows())
        ss["hist_sent"] = version

    try:
        value = _component(key="pl_store", store_key=STORE_KEY, payload=payload, version=version, default=None)
    except Exception:
        # Custom components need pyarrow. If it cannot load (for example a Windows policy blocks its DLL),
        # keep the app working and fall back to session-only history.
        ss["store_broken"] = True
        ss["store_ok"] = False
        return

    if not hydrated and isinstance(value, dict):
        ss["hist_hydrated"] = True
        ss["store_ok"] = bool(value.get("ok", False))
        merged = history.merge(value.get("rows", []))
        ss["hist_sent"] = None                          # write the merged list back on the next run
        if merged:
            st.rerun()
