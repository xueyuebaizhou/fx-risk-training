from __future__ import annotations

import streamlit as st

from ..risk import validate_inputs
from ..services import get_simulation_result
from ..simulation import compare_hedge_strategies


def require_model() -> bool:
    if st.session_state.get("model_result") is None:
        st.warning("请先在“02 汇率数据与 AI 模型”页面运行模型。")
        return False
    return True


def ensure_simulation():
    if not require_model():
        return None
    validate_inputs(
        st.session_state.amount,
        st.session_state.term_days,
        st.session_state.budget_rate,
        st.session_state.spot_rate,
        st.session_state.forward_rate,
        st.session_state.hedge_ratio,
    )
    if st.session_state.get("simulation_result") is None:
        garch = st.session_state.model_result.garch
        with st.spinner("正在使用 GARCH 参数生成 10,000 条可复现教学情景……"):
            st.session_state.simulation_result = get_simulation_result(
                float(st.session_state.spot_rate),
                int(st.session_state.term_days),
                float(garch.daily_drift),
                float(garch.daily_volatility),
            )
    simulation = st.session_state.simulation_result
    st.session_state.strategy_table = compare_hedge_strategies(
        simulation.terminal_rates,
        float(st.session_state.amount),
        float(st.session_state.budget_rate),
        float(st.session_state.forward_rate),
    )
    return simulation
