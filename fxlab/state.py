from __future__ import annotations

import hashlib
import json

import streamlit as st

from .config import (
    DEFAULT_AMOUNT,
    DEFAULT_BUDGET_RATE,
    DEFAULT_FORWARD_RATE,
    DEFAULT_HEDGE_RATIO,
    DEFAULT_TERM_DAYS,
)

DEFAULTS = {
    "amount": DEFAULT_AMOUNT,
    "term_days": DEFAULT_TERM_DAYS,
    "budget_rate": DEFAULT_BUDGET_RATE,
    "forward_rate": DEFAULT_FORWARD_RATE,
    "hedge_ratio": DEFAULT_HEDGE_RATIO,
    "spot_rate": None,
    "fx_data": None,
    "model_result": None,
    "simulation_result": None,
    "strategy_table": None,
    "final_ratio": DEFAULT_HEDGE_RATIO,
    "decision_reason": "",
}


def initialise_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("input_fingerprint", input_fingerprint())


def input_fingerprint() -> str:
    payload = {
        key: st.session_state.get(key)
        for key in (
            "amount",
            "term_days",
            "budget_rate",
            "forward_rate",
            "hedge_ratio",
            "spot_rate",
        )
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()


def invalidate_if_inputs_changed() -> bool:
    current = input_fingerprint()
    previous = st.session_state.get("input_fingerprint")
    if previous == current:
        return False
    st.session_state["input_fingerprint"] = current
    st.session_state["simulation_result"] = None
    st.session_state["strategy_table"] = None
    return True
