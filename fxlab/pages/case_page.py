import streamlit as st

from ..risk import budget_income
from ..state import invalidate_if_inputs_changed
from ..ui import cny, data_note, page_header


def render() -> None:
    page_header(
        "STEP 01 / CASE",
        "实训案例",
        "建立统一的出口收汇案例，后续模型、风险与策略结果全部由这里的参数驱动。",
    )
    st.markdown(
        """<div class="soft-card"><span class="case-tag">中国制造业出口企业</span>
        <span class="case-tag">美元应收</span><span class="case-tag">人民币预算管理</span>
        <p style="margin-top:.9rem">企业向美国客户出口产品，未来收到美元货款。由于最终以人民币核算，USD/CNY 下跌会使同额美元兑换的人民币减少。</p></div>""",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input(
            "外币应收金额 A（USD）",
            min_value=1.0,
            step=50_000.0,
            format="%.2f",
            key="amount",
        )
    with col2:
        st.number_input(
            "结算期限 T（自然日）", min_value=1, max_value=730, step=1, key="term_days"
        )
    with col3:
        st.number_input(
            "预算汇率 B（CNY/USD）",
            min_value=0.0001,
            step=0.01,
            format="%.4f",
            key="budget_rate",
        )
    invalidate_if_inputs_changed()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("交易方向", "出口收汇")
    m2.metric("币种", "USD")
    m3.metric("当前即期汇率 S₀", f"{st.session_state.spot_rate:.4f}")
    m4.metric(
        "预算人民币收入",
        cny(budget_income(st.session_state.amount, st.session_state.budget_rate)),
    )
    data_note(st.session_state.fx_data)
    st.subheader("本次实训任务")
    st.markdown(
        "1. 读取真实 USD/CNY 数据并运行 AI 模型；2. 识别美元应收风险并形成预警；3. 比较远期套保比例；4. 完成 10,000 次情景计算；5. 提交策略选择和实验报告。"
    )
