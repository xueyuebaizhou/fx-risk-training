from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, MutableMapping
from typing import Any

import streamlit as st

from .config import (
    DEFAULT_AMOUNT,
    DEFAULT_BUDGET_RATE,
    DEFAULT_FORWARD_RATE,
    DEFAULT_HEDGE_RATIO,
    DEFAULT_TERM_DAYS,
    MODEL_RESULT_SCHEMA_VERSION,
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

STATE_SCHEMA_VERSION = 3
SCENARIO_INPUT_KEYS = (
    "amount",
    "term_days",
    "budget_rate",
    "spot_rate",
    "forward_rate",
    "hedge_ratio",
)
DERIVED_RESULT_KEYS = ("model_result", "simulation_result", "strategy_table")
MODEL_RESULT_ATTRIBUTES = (
    "xgboost",
    "garch",
    "sample_start_date",
    "sample_end_date",
    "sample_size",
)


def clear_derived_results(state: MutableMapping[str, Any]) -> None:
    """Invalidate every result that depends on the fitted model."""
    for key in DERIVED_RESULT_KEYS:
        state[key] = None


def model_result_is_current(result: object) -> bool:
    """Reject cached model objects created before the current result schema."""
    if result is None:
        return True
    return getattr(result, "schema_version", None) == MODEL_RESULT_SCHEMA_VERSION and all(
        hasattr(result, attribute) for attribute in MODEL_RESULT_ATTRIBUTES
    )


def _stored_schema_version(state: MutableMapping[str, Any]) -> int:
    try:
        return int(state.get("state_schema_version", 0) or 0)
    except (TypeError, ValueError):
        return 0


def prepare_state(state: MutableMapping[str, Any]) -> None:
    """Initialise canonical scenario state and repair values from the old widget schema."""
    for key, value in DEFAULTS.items():
        state.setdefault(key, value)
    previous_version = _stored_schema_version(state)
    if previous_version < 2:
        # The previous page-local widget could initialise F from its 0.0001 lower bound.
        if float(state.get("forward_rate") or 0.0) < 1.0:
            state["forward_rate"] = DEFAULT_FORWARD_RATE
    stale_model = not model_result_is_current(state.get("model_result"))
    if previous_version < STATE_SCHEMA_VERSION or stale_model:
        had_model_result = state.get("model_result") is not None
        clear_derived_results(state)
        if had_model_result:
            state["model_refresh_required"] = True
    state["state_schema_version"] = STATE_SCHEMA_VERSION


def prepare_widget_value(
    state: MutableMapping[str, Any],
    widget_key: str,
    input_key: str,
    to_widget: Callable[[Any], Any] | None = None,
) -> None:
    """Seed a temporary widget key without turning the canonical value into widget state."""
    if widget_key not in state:
        value = state[input_key]
        state[widget_key] = to_widget(value) if to_widget else value


def commit_widget_value(
    state: MutableMapping[str, Any],
    widget_key: str,
    input_key: str,
    from_widget: Callable[[Any], Any] | None = None,
) -> None:
    """Copy an edited temporary widget value into canonical cross-page state."""
    value = state[widget_key]
    state[input_key] = from_widget(value) if from_widget else value


def initialise_state() -> None:
    prepare_state(st.session_state)
    st.session_state.setdefault("input_fingerprint", input_fingerprint())


def input_fingerprint() -> str:
    payload = {
        key: st.session_state.get(key)
        for key in SCENARIO_INPUT_KEYS
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
