from pathlib import Path

import streamlit as st

from ..config import REPORT_DIR
from ..reporting import build_html_report, build_pdf_report, save_report
from ..ui import page_header
from .common import ensure_simulation


def render() -> None:
    page_header(
        "STEP 06 / DECISION",
        "策略评价与实验报告",
        "比较固定套保比例，提交学生决策，并生成可下载、可在本次运行中重新打开的 PDF 与 HTML 报告。",
    )
    simulation = ensure_simulation()
    if simulation is None:
        return
    table = st.session_state.strategy_table.copy()
    display = table.copy()
    display["套保比例"] = display["套保比例"].map(lambda x: f"{x:.0%}")
    for col in ["平均收入", "5%分位数收入", "收入标准差", "VaR95", "CFaR95"]:
        display[col] = display[col].map(lambda x: f"¥{x:,.2f}")
    display["Risk Ratio"] = display["Risk Ratio"].map(lambda x: f"{x:.2%}")
    display["风险下降幅度"] = display["风险下降幅度"].map(lambda x: f"{x:.1%}")
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.select_slider(
        "最终选择的远期套保比例",
        options=[0.0, 0.25, 0.5, 0.75, 1.0],
        format_func=lambda x: f"{x:.0%}",
        key="final_ratio",
    )
    st.text_area(
        "选择理由（必填）",
        placeholder="例如：在现金流稳定性与保留有利汇率变动空间之间进行权衡……",
        key="decision_reason",
        max_chars=500,
    )
    if st.button("生成并保存实验报告", type="primary", use_container_width=True):
        if not st.session_state.decision_reason.strip():
            st.error("请先填写策略选择理由。")
        else:
            try:
                html_text = build_html_report(dict(st.session_state))
                pdf_bytes = build_pdf_report(dict(st.session_state))
                html_path, pdf_path = save_report(
                    html_text,
                    pdf_bytes,
                    st.session_state.amount,
                    st.session_state.term_days,
                )
                st.session_state.last_report_html = html_text
                st.session_state.last_report_pdf = pdf_bytes
                st.session_state.last_report_name = pdf_path.stem
                st.success(f"报告已保存：{pdf_path.name} / {html_path.name}")
            except (OSError, RuntimeError, TypeError, ValueError) as exc:
                st.error(f"报告生成失败：{exc}")
    if st.session_state.get("last_report_pdf"):
        c1, c2 = st.columns(2)
        c1.download_button(
            "下载 PDF",
            st.session_state.last_report_pdf,
            f"{st.session_state.last_report_name}.pdf",
            "application/pdf",
            use_container_width=True,
        )
        c2.download_button(
            "下载 HTML",
            st.session_state.last_report_html,
            f"{st.session_state.last_report_name}.html",
            "text/html",
            use_container_width=True,
        )
    st.subheader("本次运行的历史报告")
    files = sorted(Path(REPORT_DIR).glob("*.pdf"), reverse=True)[:20]
    if not files:
        st.caption("尚未生成报告。")
    else:
        for path in files:
            st.download_button(
                path.name,
                path.read_bytes(),
                path.name,
                "application/pdf",
                key=f"history_{path.name}",
            )
