import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import SIMULATION_PATHS
from ..risk import budget_income, calculate_risk_metrics, hedged_income
from ..ui import (
    AMBER,
    CHART_PALETTE,
    CORAL,
    cny,
    page_header,
    render_chart,
    scenario_summary,
    section_label,
    style_chart,
)
from .common import ensure_simulation

DISPLAY_PATHS = 80


def _path_scenario_chart(paths: np.ndarray, spot_rate: float) -> go.Figure:
    """Build a legible multi-colour sample without changing full-sample calculations."""
    display_count = min(DISPLAY_PATHS, len(paths))
    selected = np.asarray(paths[:display_count], dtype=float)
    with_start = np.column_stack([np.full(display_count, spot_rate), selected])
    fig = go.Figure()
    for index, path in enumerate(with_start):
        fig.add_trace(
            go.Scatter(
                x=np.arange(path.size),
                y=path,
                mode="lines",
                name=f"路径 {index + 1:02d}",
                line={
                    "width": 0.85,
                    "color": CHART_PALETTE[index % len(CHART_PALETTE)],
                },
                opacity=0.24,
                showlegend=False,
                hovertemplate=(
                    "交易日 %{x}<br>USD/CNY %{y:.4f}"
                    f"<extra>路径 {index + 1:02d}</extra>"
                ),
            )
        )
    fig.update_layout(
        title=f"展示前 {display_count} 条路径（指标仍基于 {SIMULATION_PATHS:,} 条）",
        xaxis_title="交易日",
        yaxis_title="USD/CNY",
        height=380,
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
    )
    return fig


def _distribution_charts(
    terminal_rates: np.ndarray,
    incomes: np.ndarray,
    hedge_ratio: float,
) -> tuple[go.Figure, go.Figure]:
    terminal_values = np.asarray(terminal_rates, dtype=float)
    income_values = np.asarray(incomes, dtype=float) / 10_000
    terminal_mean = float(np.mean(terminal_values))
    income_mean = float(np.mean(income_values))
    income_q05 = float(np.quantile(income_values, 0.05))

    rate_fig = px.histogram(
        x=terminal_values,
        nbins=60,
        labels={"x": "到期 USD/CNY"},
        title="到期汇率分布",
    )
    rate_fig.add_vline(
        x=terminal_mean,
        line_dash="dash",
        line_color=AMBER,
        line_width=2,
        annotation_text=f"均值 {terminal_mean:.4f}",
        annotation_position="top right",
    )
    rate_fig.update_yaxes(title_text="模拟次数")
    rate_fig.update_layout(
        height=350,
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
    )

    income_fig = px.histogram(
        x=income_values,
        nbins=60,
        labels={"x": "人民币收入（万元）"},
        title=f"{hedge_ratio:.0%} 套保收入分布",
    )
    if np.isclose(income_mean, income_q05):
        income_fig.add_vline(
            x=income_mean,
            line_dash="dash",
            line_color=CORAL,
            line_width=2,
            annotation_text=f"均值 = 5%分位 {income_mean:.2f} 万元",
            annotation_position="top right",
        )
    else:
        income_fig.add_vline(
            x=income_mean,
            line_dash="dash",
            line_color=AMBER,
            line_width=2,
            annotation_text=f"均值 {income_mean:.2f} 万元",
            annotation_position="top right",
        )
        income_fig.add_vline(
            x=income_q05,
            line_dash="dash",
            line_color=CORAL,
            line_width=2,
            annotation_text=f"5%分位 {income_q05:.2f} 万元",
            annotation_position="top left",
        )
    income_fig.update_yaxes(title_text="模拟次数")
    income_fig.update_layout(
        height=350,
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
    )
    return style_chart(rate_fig), style_chart(income_fig)


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
    section_label(
        "路径情景",
        f"多色可视化抽样 {DISPLAY_PATHS} 条 · 风险指标使用全部 {SIMULATION_PATHS:,} 条",
    )
    render_chart(_path_scenario_chart(simulation.paths, st.session_state.spot_rate))
    incomes = hedged_income(
        st.session_state.amount,
        st.session_state.hedge_ratio,
        st.session_state.forward_rate,
        simulation.terminal_rates,
    )
    metrics = calculate_risk_metrics(
        incomes,
        budget_income(st.session_state.amount, st.session_state.budget_rate),
        st.session_state.amount * st.session_state.spot_rate,
    )
    rate_fig, income_fig = _distribution_charts(
        simulation.terminal_rates,
        incomes,
        st.session_state.hedge_ratio,
    )
    c1, c2 = st.columns(2)
    with c1:
        render_chart(rate_fig)
    with c2:
        render_chart(income_fig)
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
    section_label("固定比例策略比较", "统一终值样本 · 结果可直接横向比较")
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
    fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 45, "b": 10}, yaxis_title="CNY")
    render_chart(fig)
