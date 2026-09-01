import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import SIMULATION_PATHS
from ..risk import budget_income, calculate_risk_metrics, hedged_income
from ..ui import cny, page_header, scenario_summary
from .common import ensure_simulation


def render() -> None:
    page_header(
        "STEP 05 / MONTE CARLO",
        "蒙特卡洛情景模拟",
        "使用真实历史收益率与 GARCH 波动率参数生成固定种子的未来汇率教学情景。",
    )
    simulation = ensure_simulation()
    if simulation is None:
        return
    scenario_summary(st.session_state)
    st.warning(
        f"以下未来路径均为模型生成的教学情景，不是真实未来行情。完整指标使用全部 {SIMULATION_PATHS:,} 条路径。"
    )
    st.caption(
        f"期限：{st.session_state.term_days} 个自然日 → {simulation.trading_days} 个交易日；随机种子：{simulation.seed}；日漂移：{simulation.daily_drift:.6%}；GARCH 日波动率：{simulation.daily_volatility:.4%}。"
    )
    display_count = 80
    selected = simulation.paths[:display_count]
    with_start = np.column_stack(
        [np.full(display_count, st.session_state.spot_rate), selected]
    )
    fig = go.Figure()
    for path in with_start:
        fig.add_trace(
            go.Scatter(
                x=np.arange(path.size),
                y=path,
                mode="lines",
                line={"width": 0.7},
                opacity=0.25,
                showlegend=False,
            )
        )
    fig.update_layout(
        title=f"展示前 {display_count} 条路径（指标仍基于 10,000 条）",
        xaxis_title="交易日",
        yaxis_title="USD/CNY",
        height=380,
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
    )
    st.plotly_chart(fig, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            x=simulation.terminal_rates,
            nbins=60,
            labels={"x": "到期 USD/CNY", "count": "情景数"},
            title="到期汇率分布",
        )
        fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 45, "b": 10})
        st.plotly_chart(fig, width="stretch")
    with c2:
        incomes = hedged_income(
            st.session_state.amount,
            st.session_state.hedge_ratio,
            st.session_state.forward_rate,
            simulation.terminal_rates,
        )
        fig = px.histogram(
            x=incomes / 10000,
            nbins=60,
            labels={"x": "人民币收入（万元）", "count": "情景数"},
            title=f"{st.session_state.hedge_ratio:.0%} 套保收入分布",
        )
        fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 45, "b": 10})
        st.plotly_chart(fig, width="stretch")
    metrics = calculate_risk_metrics(
        incomes,
        budget_income(st.session_state.amount, st.session_state.budget_rate),
        st.session_state.amount * st.session_state.spot_rate,
    )
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("平均收入", cny(metrics.mean_income))
    m2.metric("5%分位数收入", cny(metrics.q05_income))
    m3.metric("收入标准差", cny(metrics.income_std))
    m4.metric("VaR / CFaR", f"{cny(metrics.var95)} / {cny(metrics.cfar95)}")
    table = st.session_state.strategy_table.copy()
    display = table.copy()
    display["套保比例"] = display["套保比例"].map(lambda x: f"{x:.0%}")
    for col in ["平均收入", "5%分位数收入", "收入标准差", "VaR95", "CFaR95"]:
        display[col] = display[col].map(lambda x: f"{x:,.2f}")
    display["Risk Ratio"] = display["Risk Ratio"].map(lambda x: f"{x:.2%}")
    display["风险下降幅度"] = display["风险下降幅度"].map(lambda x: f"{x:.1%}")
    st.subheader("固定比例策略比较")
    st.dataframe(display, width="stretch", hide_index=True)
    chart = table.copy()
    chart["套保比例"] = chart["套保比例"].map(lambda x: f"{x:.0%}")
    fig = px.bar(
        chart,
        x="套保比例",
        y=["CFaR95", "收入标准差"],
        barmode="group",
        title="尾部风险与收入波动比较",
    )
    fig.update_layout(
        height=350, margin={"l": 10, "r": 10, "t": 45, "b": 10}, yaxis_title="CNY"
    )
    st.plotly_chart(fig, width="stretch")
