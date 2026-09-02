from __future__ import annotations

import html
from collections.abc import Sequence

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

INK = "#24212F"
MUTED = "#716C7D"
PRIMARY = "#7765E7"
PRIMARY_LIGHT = "#A79BFA"
EMERALD = "#168A63"
CORAL = "#D65864"
AMBER = "#C6832B"
GRID = "#EAE7F0"
CHART_PALETTE: Sequence[str] = (
    PRIMARY,
    EMERALD,
    CORAL,
    AMBER,
    "#4B76B8",
    PRIMARY_LIGHT,
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #24212f;
            --muted: #716c7d;
            --primary: #7765e7;
            --primary-deep: #5f4dd1;
            --lavender: #eeeafe;
            --lavender-soft: #f7f5ff;
            --emerald: #168a63;
            --coral: #d65864;
            --amber: #c6832b;
            --line: #e6e2ec;
            --canvas: #f8f7fb;
            --panel: #ffffff;
            --sidebar: #282342;
        }
        html, body, [class*="css"], .stApp {
            font-family: Inter, Aptos, "Segoe UI", "Microsoft YaHei", sans-serif;
        }
        .stApp { background: var(--canvas); color: var(--ink); }
        .block-container {
            max-width: 1240px;
            padding: 2.1rem 2.6rem 4rem;
        }
        h1, h2, h3, p { color: var(--ink); }
        h3 {
            font-size: 1.12rem !important;
            font-weight: 700 !important;
            letter-spacing: -.015em;
            margin-top: 1.7rem !important;
        }
        hr { border-color: rgba(255,255,255,.11) !important; }

        /* Institutional navigation */
        [data-testid="stSidebar"] { background: var(--sidebar); border-right: 0; }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
        [data-testid="stSidebar"] * { color: #f7f5ff; }
        .brand-shell {
            display: flex;
            align-items: center;
            gap: .8rem;
            padding: .45rem .2rem 1.55rem;
        }
        .brand-mark {
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 11px;
            background: #8d7cf3;
            color: white;
            font-size: .9rem;
            font-weight: 800;
            letter-spacing: .04em;
            box-shadow: 0 8px 20px rgba(13,8,38,.24);
        }
        .brand-name {
            color: white;
            font-size: .97rem;
            font-weight: 760;
            letter-spacing: .035em;
        }
        .brand-subtitle {
            color: #bbb4d6;
            font-size: .72rem;
            margin-top: .18rem;
            line-height: 1.45;
        }
        .nav-label {
            color: #9189ad;
            font-size: .66rem;
            font-weight: 700;
            letter-spacing: .15em;
            margin: 0 .5rem .55rem;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] { gap: .32rem; }
        [data-testid="stSidebar"] label[data-baseweb="radio"],
        [data-testid="stSidebar"] [data-testid="stRadioOption"] {
            min-height: 42px;
            padding: .58rem .72rem;
            border-radius: 9px;
            transition: background .15s ease, color .15s ease;
        }
        [data-testid="stSidebar"] label[data-baseweb="radio"]:hover,
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover,
        [data-testid="stSidebar"] [data-testid="stRadioOption"][data-hovered="true"] {
            background: rgba(255,255,255,.07);
        }
        [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked),
        [data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked),
        [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {
            background: rgba(141,124,243,.22);
            box-shadow: inset 3px 0 0 #9b8cf7;
        }
        [data-testid="stSidebar"] label[data-baseweb="radio"] p,
        [data-testid="stSidebar"] [data-testid="stRadioOption"] p {
            font-size: .85rem;
            font-weight: 530;
        }
        .sidebar-market {
            margin: 1.25rem .2rem 0;
            padding: 1rem .85rem;
            border: 1px solid rgba(255,255,255,.10);
            border-radius: 10px;
            background: rgba(255,255,255,.035);
        }
        .sidebar-market-label {
            color: #948aad;
            font-size: .63rem;
            font-weight: 700;
            letter-spacing: .14em;
        }
        .sidebar-market-pair {
            color: #fff;
            font-size: 1.05rem;
            font-weight: 700;
            margin: .3rem 0 .2rem;
        }
        .sidebar-market-meta {
            color: #bdb6d5;
            font-size: .72rem;
            line-height: 1.55;
        }

        /* Page hierarchy */
        .page-intro {
            margin: .2rem 0 1.55rem;
            padding-bottom: 1.15rem;
            border-bottom: 1px solid var(--line);
        }
        .page-kicker {
            color: var(--primary);
            font-size: .68rem;
            font-weight: 760;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }
        .page-title {
            color: var(--ink);
            font-size: clamp(1.75rem, 3vw, 2.35rem);
            font-weight: 720;
            letter-spacing: -.035em;
            line-height: 1.15;
            margin: 0 0 .45rem;
        }
        .page-desc {
            color: var(--muted);
            font-size: .93rem;
            line-height: 1.7;
            max-width: 780px;
        }
        .section-label {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 1rem;
            margin: 1.8rem 0 .75rem;
        }
        .section-label-title {
            color: var(--ink);
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: -.015em;
        }
        .section-label-note { color: var(--muted); font-size: .76rem; }

        /* Data surfaces */
        .soft-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 13px;
            padding: 1.15rem 1.25rem;
            margin: .5rem 0 1.15rem;
            box-shadow: 0 8px 24px rgba(49,39,91,.045);
        }
        .soft-card p { color: #4f4a59; line-height: 1.7; }
        .case-tag {
            display: inline-block;
            background: var(--lavender-soft);
            color: #6253c7;
            border: 1px solid #e6e0ff;
            border-radius: 6px;
            padding: .3rem .62rem;
            margin-right: .38rem;
            font-size: .76rem;
            font-weight: 650;
        }
        .formula {
            background: var(--lavender-soft);
            border: 1px solid #e5e0fb;
            border-left: 3px solid var(--primary);
            padding: .9rem 1rem;
            border-radius: 8px;
            color: #403a53;
            font-family: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
            font-size: .84rem;
            line-height: 1.7;
        }
        .source-note {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: .65rem;
            align-items: start;
            color: #686275;
            font-size: .75rem;
            line-height: 1.65;
            margin: 1rem 0 .5rem;
            padding: .75rem .9rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,.62);
        }
        .source-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--emerald);
            box-shadow: 0 0 0 4px rgba(22,138,99,.10);
            margin-top: .35rem;
        }
        .source-note strong { color: #403b4c; font-weight: 680; }
        .scenario-strip {
            display: grid;
            grid-template-columns: repeat(6,minmax(0,1fr));
            border: 1px solid var(--line);
            border-radius: 10px;
            background: #fff;
            margin: .35rem 0 1rem;
            overflow: hidden;
        }
        .scenario-item { padding: .62rem .72rem; border-right: 1px solid var(--line); }
        .scenario-item:last-child { border-right: 0; }
        .scenario-key {
            display: block;
            color: #948ea0;
            font-size: .61rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
        }
        .scenario-value {
            display: block;
            color: var(--ink);
            font-size: .79rem;
            font-weight: 680;
            margin-top: .16rem;
            white-space: nowrap;
        }
        .risk-panel {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            border: 1px solid var(--line);
            border-radius: 10px;
            background: #fff;
            padding: .78rem .95rem;
            margin: .75rem 0;
        }
        .risk-panel-label { color: var(--muted); font-size: .8rem; }
        .risk-pill {
            border-radius: 6px;
            padding: .27rem .58rem;
            font-size: .75rem;
            font-weight: 750;
        }
        .risk-low { color: #0e7654; background: #e9f7f1; }
        .risk-mid { color: #9a5e10; background: #fff4df; }
        .risk-high { color: #b83d4a; background: #fdecee; }
        .task-list {
            display: grid;
            grid-template-columns: repeat(5,minmax(0,1fr));
            gap: .65rem;
            margin-top: .8rem;
        }
        .task-item {
            min-height: 100px;
            padding: .85rem;
            border: 1px solid var(--line);
            border-radius: 10px;
            background: #fff;
            color: #514b5d;
            font-size: .77rem;
            line-height: 1.55;
        }
        .task-number {
            display: block;
            color: var(--primary);
            font-size: .7rem;
            font-weight: 760;
            letter-spacing: .08em;
            margin-bottom: .45rem;
        }

        /* Native Streamlit components */
        div[data-testid="stMetric"] {
            min-height: 112px;
            background: var(--panel);
            border: 1px solid var(--line);
            padding: .82rem .9rem;
            border-radius: 11px;
            box-shadow: 0 6px 18px rgba(49,39,91,.035);
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
            color: #6f6979;
            font-size: .75rem;
            font-weight: 600;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--ink);
            font-size: 1.75rem;
            font-weight: 560;
            letter-spacing: -.035em;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: .72rem; }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        [data-testid="stNumberInputContainer"],
        [data-testid="stTextInputRootElement"],
        [data-testid="stTextAreaRootElement"],
        [data-testid="stTextArea"] textarea {
            background: #fff !important;
            border-color: var(--line) !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        [data-testid="stNumberInputContainer"]:focus-within,
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stTextAreaRootElement"]:focus-within,
        [data-testid="stTextArea"] textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(119,101,231,.12) !important;
        }
        [data-testid="stNumberInputField"] { background: transparent !important; }
        .stButton > button, .stDownloadButton > button {
            min-height: 2.65rem;
            border-radius: 8px;
            border: 1px solid #dcd7e7;
            background: #fff;
            color: #393343;
            font-weight: 650;
            box-shadow: none;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            color: var(--primary-deep);
            border-color: var(--primary);
            background: var(--lavender-soft);
        }
        .stButton > button[kind="primary"] {
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }
        .stButton > button[kind="primary"]:hover {
            background: var(--primary-deep);
            border-color: var(--primary-deep);
            color: white;
        }
        [data-testid="stSlider"] [role="slider"],
        [data-testid="stSlider"] input[type="range"] {
            accent-color: var(--primary) !important;
        }
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div {
            background: var(--lavender) !important;
        }
        [data-testid="stProgress"] > div > div > div > div {
            background: var(--primary) !important;
        }
        [data-testid="stTabs"] {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: .35rem .8rem .8rem;
            box-shadow: 0 6px 20px rgba(49,39,91,.03);
        }
        [data-baseweb="tab-list"] { gap: 1.15rem; border-bottom: 1px solid var(--line); }
        [data-baseweb="tab"] { color: var(--muted); font-size: .8rem; font-weight: 650; }
        [aria-selected="true"][data-baseweb="tab"] { color: var(--primary) !important; }
        [data-baseweb="tab-highlight"] { background: var(--primary) !important; }
        div[data-testid="stPlotlyChart"] {
            background: #fff;
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: .28rem;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(49,39,91,.03);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            background: #fff;
        }
        [data-testid="stAlert"] {
            border-radius: 9px;
            border-width: 1px;
            box-shadow: none;
        }
        [data-testid="stAlertContentInfo"] {
            background: #f1eeff !important;
            color: #4d426e !important;
        }
        [data-testid="stExpander"] {
            border-color: var(--line);
            border-radius: 9px;
            background: #fff;
        }
        [data-testid="stCaptionContainer"] p { color: var(--muted); }
        [data-testid="stHeader"] { background: rgba(248,247,251,.88); }
        [data-testid="stToolbarActions"] { display: none !important; }

        @media (max-width: 900px) {
            .block-container { padding: 1.4rem 1.05rem 3rem; }
            .scenario-strip { grid-template-columns: repeat(3,1fr); }
            .scenario-item:nth-child(3) { border-right: 0; }
            .scenario-item:nth-child(-n+3) { border-bottom: 1px solid var(--line); }
            .task-list { grid-template-columns: 1fr 1fr; }
            .page-title { font-size: 1.75rem; }
        }
        @media (max-width: 560px) {
            .scenario-strip { grid-template-columns: repeat(2,1fr); }
            .scenario-item { border-bottom: 1px solid var(--line); }
            .scenario-item:nth-child(even) { border-right: 0; }
            .scenario-item:nth-last-child(-n+2) { border-bottom: 0; }
            .task-list { grid-template-columns: 1fr; }
            .section-label { align-items: flex-start; flex-direction: column; gap: .2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_navigation() -> str:
    with st.sidebar:
        st.markdown(
            '<div class="brand-shell"><div class="brand-mark">FX</div>'
            '<div><div class="brand-name">FX RISK LAB</div>'
            f'<div class="brand-subtitle">{html.escape(APP_TITLE)}</div></div></div>'
            '<div class="nav-label">TRAINING WORKFLOW</div>',
            unsafe_allow_html=True,
        )
        page = st.radio("实训流程", PAGES, label_visibility="collapsed")
        st.markdown(
            '<div class="sidebar-market"><div class="sidebar-market-label">MARKET / CASE</div>'
            '<div class="sidebar-market-pair">USD / CNY</div>'
            '<div class="sidebar-market-meta">出口收汇 · 人民币预算管理<br>'
            "真实历史数据 · 模型教学情景</div></div>",
            unsafe_allow_html=True,
        )
    return page


def page_header(step: str, title: str, description: str) -> None:
    st.markdown(
        '<section class="page-intro">'
        f'<div class="page-kicker">{html.escape(step)}</div>'
        f'<h1 class="page-title">{html.escape(title)}</h1>'
        f'<div class="page-desc">{html.escape(description)}</div>'
        "</section>",
        unsafe_allow_html=True,
    )


def section_label(title: str, note: str = "") -> None:
    note_html = f'<div class="section-label-note">{html.escape(note)}</div>' if note else ""
    st.markdown(
        '<div class="section-label">'
        f'<div class="section-label-title">{html.escape(title)}</div>{note_html}</div>',
        unsafe_allow_html=True,
    )


def data_note(data) -> None:
    st.markdown(
        '<div class="source-note"><span class="source-dot"></span><div>'
        f"<strong>真实市场数据</strong>　{html.escape(data.source)}<br>"
        f"样本范围：{data.start_date} 至 {data.end_date}　·　"
        f"读取时间：{html.escape(data.retrieved_at)}　·　{html.escape(data.mode)}</div></div>",
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
    items = (
        ("A · 应收金额", f"USD {float(state.amount):,.0f}"),
        ("T · 期限", f"{int(state.term_days)} 天"),
        ("B · 预算汇率", f"{float(state.budget_rate):.4f}"),
        ("S₀ · 即期汇率", f"{float(state.spot_rate):.4f}"),
        ("F · 远期汇率", f"{float(state.forward_rate):.4f}"),
        ("h · 套保比例", f"{float(state.hedge_ratio):.0%}"),
    )
    cells = "".join(
        '<div class="scenario-item">'
        f'<span class="scenario-key">{html.escape(key)}</span>'
        f'<span class="scenario-value">{html.escape(value)}</span></div>'
        for key, value in items
    )
    st.markdown(f'<div class="scenario-strip">{cells}</div>', unsafe_allow_html=True)


def risk_badge(level: str) -> None:
    css = {"低风险": "risk-low", "中风险": "risk-mid", "高风险": "risk-high"}.get(level, "")
    st.markdown(
        '<div class="risk-panel"><span class="risk-panel-label">企业敞口风险等级</span>'
        f'<span class="risk-pill {css}">{html.escape(level)}</span></div>',
        unsafe_allow_html=True,
    )


def style_chart(fig):
    """Apply the shared institutional chart theme without changing chart data."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        colorway=list(CHART_PALETTE),
        font={
            "family": 'Inter, Aptos, "Segoe UI", "Microsoft YaHei", sans-serif',
            "color": INK,
            "size": 12,
        },
        title={"font": {"color": INK, "size": 15}, "x": 0.025, "xanchor": "left"},
        legend={
            "bgcolor": "rgba(255,255,255,.84)",
            "bordercolor": GRID,
            "borderwidth": 1,
            "font": {"color": MUTED, "size": 11},
        },
        hoverlabel={"bgcolor": INK, "font": {"color": "#FFFFFF", "size": 12}},
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=GRID,
        tickcolor=GRID,
        tickfont={"color": MUTED, "size": 10},
        title_font={"color": MUTED, "size": 11},
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor=GRID,
        gridwidth=1,
        showline=False,
        tickfont={"color": MUTED, "size": 10},
        title_font={"color": MUTED, "size": 11},
        zeroline=False,
    )
    for index, trace in enumerate(fig.data):
        color = CHART_PALETTE[index % len(CHART_PALETTE)]
        if trace.type == "histogram":
            trace.marker.color = PRIMARY
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 0.35
            trace.opacity = 0.92
        elif trace.type == "bar":
            trace.marker.color = color
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 0.4
        elif trace.type == "scatter":
            default_plotly_colors = {None, "#636efa", "#EF553B", "#00cc96", "#ab63fa"}
            if trace.line.color in default_plotly_colors:
                trace.line.color = color
            if not trace.line.width:
                trace.line.width = 1.8
    return fig


def render_chart(fig) -> None:
    st.plotly_chart(
        style_chart(fig),
        width="stretch",
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "responsive": True,
        },
    )
