from collections.abc import MutableMapping

import streamlit as st

from ..config import MAX_USDCNY_RATE, MIN_USDCNY_RATE
from ..risk import budget_income, calculate_risk_metrics, hedge_effect, hedged_income
from ..state import commit_widget_value, invalidate_if_inputs_changed, prepare_widget_value
from ..ui import cny, page_header, scenario_summary, section_label
from .common import ensure_simulation


def apply_quick_ratio(state: MutableMapping[str, object], ratio_percent: int) -> None:
    state["_hedge_ratio_slider"] = ratio_percent
    state["hedge_ratio"] = ratio_percent / 100


def _apply_quick_ratio(ratio_percent: int) -> None:
    apply_quick_ratio(st.session_state, ratio_percent)


def _commit_forward_rate() -> None:
    commit_widget_value(st.session_state, "_forward_rate_input", "forward_rate")


def _commit_hedge_ratio() -> None:
    commit_widget_value(
        st.session_state,
        "_hedge_ratio_slider",
        "hedge_ratio",
        lambda value: int(value) / 100,
    )


def render() -> None:
    page_header(
        "STEP 04 / HEDGE SANDBOX",
        "避险策略沙盘",
        "仅比较不套保与远期结汇，观察套保比例如何改变人民币收入和尾部风险。",
    )
    prepare_widget_value(st.session_state, "_forward_rate_input", "forward_rate")
    prepare_widget_value(
        st.session_state,
        "_hedge_ratio_slider",
        "hedge_ratio",
        lambda value: round(float(value) * 100),
    )
    section_label("策略参数", "调整远期报价与连续套保比例")
    c1, c2 = st.columns([1, 1.35])
    with c1:
        st.number_input(
            "教学案例远期报价 F（CNY/USD）",
            min_value=MIN_USDCNY_RATE,
            max_value=MAX_USDCNY_RATE,
            step=0.01,
            format="%.4f",
            key="_forward_rate_input",
            on_change=_commit_forward_rate,
        )
        st.caption("该数值由课程案例设定，不是实时银行报价。")
    with c2:
        st.slider(
            "连续套保比例 h",
            0,
            100,
            key="_hedge_ratio_slider",
            format="%d%%",
            on_change=_commit_hedge_ratio,
        )
    st.caption("快捷比例")
    cols = st.columns(5)
    for col, ratio in zip(cols, (0, 25, 50, 75, 100), strict=True):
        col.button(
            f"{ratio}%",
            width="stretch",
            key=f"quick_{ratio}",
            on_click=_apply_quick_ratio,
            args=(ratio,),
        )
    invalidate_if_inputs_changed()
    scenario_summary(st.session_state)
    simulation = ensure_simulation()
    if simulation is None:
        return
    section_label("策略结果", "同一组情景下与完全不套保基准比较")
    h = st.session_state.hedge_ratio
    incomes = hedged_income(
        st.session_state.amount,
        h,
        st.session_state.forward_rate,
        simulation.terminal_rates,
    )
    r_budget = budget_income(st.session_state.amount, st.session_state.budget_rate)
    spot_reference_income = st.session_state.amount * st.session_state.spot_rate
    metrics = calculate_risk_metrics(incomes, r_budget, spot_reference_income)
    baseline = calculate_risk_metrics(
        hedged_income(
            st.session_state.amount,
            0,
            st.session_state.forward_rate,
            simulation.terminal_rates,
        ),
        r_budget,
        spot_reference_income,
    )
    reduction = (baseline.cfar95 - metrics.cfar95) / baseline.cfar95 if baseline.cfar95 else 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("锁定美元金额", f"${st.session_state.amount * h:,.0f}")
    m2.metric("平均人民币收入", cny(metrics.mean_income))
    m3.metric("CFaR₉₅", cny(metrics.cfar95))
    m4.metric("CFaR 风险下降", f"{reduction:.1%}")
    mean_terminal = float(simulation.terminal_rates.mean())
    mean_effect = float(
        hedge_effect(st.session_state.amount, h, st.session_state.forward_rate, mean_terminal)
    )
    st.markdown(
        f"<div class='formula'>R_hedged = A[hF + (1-h)S_T]<br>在本次情景平均到期汇率 {mean_terminal:.4f} 下，远期相对完全不套保的收入差额为 {cny(mean_effect)}。</div>",
        unsafe_allow_html=True,
    )
    st.info(
        "远期套保的目标是降低人民币现金流波动和尾部风险。放弃部分有利汇率变动收益不等同于策略“亏损”。"
    )
