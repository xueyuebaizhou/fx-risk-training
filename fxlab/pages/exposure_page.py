import streamlit as st

from ..risk import budget_income, calculate_risk_metrics, unhedged_income
from ..ui import cny, page_header, risk_badge, section_label
from .common import ensure_simulation


def render() -> None:
    page_header(
        "STEP 03 / EXPOSURE",
        "外汇风险敞口与智能预警",
        "识别美元应收敞口，并用未套保收入教学情景计算 VaR、CFaR 与风险等级。",
    )
    simulation = ensure_simulation()
    if simulation is None:
        return
    r_budget = budget_income(st.session_state.amount, st.session_state.budget_rate)
    incomes = unhedged_income(st.session_state.amount, simulation.terminal_rates)
    spot_reference_income = st.session_state.amount * st.session_state.spot_rate
    metrics = calculate_risk_metrics(incomes, r_budget, spot_reference_income)
    st.markdown(
        "<div class='soft-card'><b>敞口识别：</b>出口企业未来收到 USD，属于美元应收敞口。USD/CNY 下跌时，结汇人民币收入减少。</div>",
        unsafe_allow_html=True,
    )
    section_label("核心风险指标", "未套保收入情景 · 95% 置信水平")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("预算人民币收入", cny(r_budget))
    m2.metric(
        "未套保平均收入",
        cny(metrics.mean_income),
        cny(metrics.mean_income - r_budget),
        delta_color="normal",
    )
    m3.metric("95% VaR", cny(metrics.var95))
    m4.metric("95% CFaR", cny(metrics.cfar95))
    risk_badge(metrics.risk_level)
    st.progress(
        min(metrics.risk_ratio / 0.08, 1.0),
        text=f"Risk Ratio = CFaR₉₅ / R_budget = {metrics.risk_ratio:.2%}",
    )
    st.markdown(
        "<div class='formula'>汇率损失 L = A × S₀ − R；VaR₉₅ = max[Q₉₅%(L), 0]"
        "<br>CFaR₉₅ = max[R_budget − Q₅%(R), 0]（相对预算现金流缺口）</div>",
        unsafe_allow_html=True,
    )
    st.warning(
        "风险阈值为本系统用于教学实训和策略比较的内部规则，不代表监管部门、银行或其他金融机构的统一风险划分标准。"
    )
