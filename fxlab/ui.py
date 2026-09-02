from __future__ import annotations

import html

import streamlit as st

from .config import APP_TITLE

PAGES = (
    "01 实训案例",
    "02 汇率数据与 AI 模型",
    "03 风险敞口与智能预警",
    "04 避险策略沙盘",
    "05 蒙特卡洛情景模拟",
    "06 策略评价与实验报告",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#17324d; --blue:#1f5f99; --pale:#eef5fb; --line:#dce6ef; }
        .stApp { background:#f7f9fc; color:#26384a; }
        .block-container { max-width:1180px; padding-top:1.6rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:#102d46; }
        [data-testid="stSidebar"] * { color:#eef6fc; }
        [data-testid="stSidebar"] .stRadio label { padding:.36rem .25rem; }
        .app-brand { color:#fff; font-size:1.05rem; font-weight:700; line-height:1.55; margin:.4rem 0 1.2rem; }
        .page-kicker { color:#1f5f99; font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
        .page-title { color:#17324d; font-size:2rem; font-weight:760; margin:.15rem 0 .25rem; }
        .page-desc { color:#637487; font-size:.98rem; margin-bottom:1.25rem; }
        .soft-card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.25rem; margin:.55rem 0 1rem; box-shadow:0 5px 18px rgba(22,50,77,.045); }
        .case-tag { display:inline-block; background:#e9f2fa; color:#1f5f99; border-radius:999px; padding:.28rem .68rem; margin-right:.35rem; font-size:.82rem; }
        .formula { background:#f0f5f9; border-left:4px solid #3278b5; padding:.8rem 1rem; border-radius:8px; color:#17324d; }
        .source-note { color:#607286; font-size:.82rem; }
        div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:.8rem; border-radius:12px; }
        div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
        .risk-low { color:#16794a; font-weight:750; }
        .risk-mid { color:#b16708; font-weight:750; }
        .risk-high { color:#b3261e; font-weight:750; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_navigation() -> str:
    with st.sidebar:
        st.markdown(
            f'<div class="app-brand">{html.escape(APP_TITLE)}</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("实训流程", PAGES, label_visibility="collapsed")
        st.divider()
        st.caption("USD/CNY · 出口收汇 · 教学实训")
        st.caption("历史行情来自可追溯真实数据；未来路径为模型生成的教学情景。")
    return page


def page_header(step: str, title: str, description: str) -> None:
    st.markdown(
        f'<div class="page-kicker">{html.escape(step)}</div>'
        f'<div class="page-title">{html.escape(title)}</div>'
        f'<div class="page-desc">{html.escape(description)}</div>',
        unsafe_allow_html=True,
    )


def data_note(data) -> None:
    st.markdown(
        f'<div class="source-note">数据来源：{html.escape(data.source)}<br>'
        f"样本范围：{data.start_date} 至 {data.end_date}　|　"
        f"本次读取：{html.escape(data.retrieved_at)}　|　模式：{html.escape(data.mode)}</div>",
        unsafe_allow_html=True,
    )


def cny(value: float) -> str:
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= 100_000_000:
        return f"{sign}¥{magnitude / 100_000_000:,.2f} 亿"
    if magnitude >= 10_000:
        return f"{sign}¥{magnitude / 10_000:,.2f} 万"
    return f"{sign}¥{magnitude:,.2f}"


def scenario_summary(state) -> None:
    st.caption(
        "统一案例参数｜"
        f"A=${float(state.amount):,.2f}｜T={int(state.term_days)} 天｜"
        f"B={float(state.budget_rate):.4f}｜S₀={float(state.spot_rate):.4f}｜"
        f"F={float(state.forward_rate):.4f}｜h={float(state.hedge_ratio):.0%}"
    )


def risk_badge(level: str) -> None:
    css = {"低风险": "risk-low", "中风险": "risk-mid", "高风险": "risk-high"}.get(level, "")
    st.markdown(
        f'企业敞口风险：<span class="{css}">{html.escape(level)}</span>',
        unsafe_allow_html=True,
    )
