import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import MODEL_RESULT_SCHEMA_VERSION
from ..services import get_model_result
from ..state import clear_derived_results, model_result_is_current
from ..ui import data_note, page_header


def _volatility_state(result) -> tuple[str, float]:
    history = np.asarray(result.conditional_volatility)
    percentile = float(np.mean(history <= result.daily_volatility))
    if percentile < 1 / 3:
        return "低", percentile
    if percentile < 2 / 3:
        return "中", percentile
    return "高", percentile


def render() -> None:
    page_header(
        "STEP 02 / DATA & AI",
        "汇率数据与 AI 模型",
        "同一套真实日频数据用于走势、特征、XGBoost 测试、GARCH 波动率与后续情景参数。",
    )
    data = st.session_state.fx_data
    data_note(data)
    if st.session_state.pop("model_refresh_required", False):
        st.info("应用模型结构已更新，旧结果已安全清除；请重新运行模型。")
    frame = data.frame
    tabs = st.tabs(["历史汇率", "日对数收益率", "20日滚动年化波动率"])
    with tabs[0]:
        fig = px.line(frame, x="date", y="rate", labels={"date": "日期", "rate": "USD/CNY"})
        fig.update_layout(height=340, margin={"l": 10, "r": 10, "t": 25, "b": 10})
        st.plotly_chart(fig, width="stretch")
    with tabs[1]:
        returns = frame.dropna(subset=["log_return"]).copy()
        returns["收益率（%）"] = returns["log_return"] * 100
        fig = px.line(returns, x="date", y="收益率（%）", labels={"date": "日期"})
        fig.update_layout(height=340, margin={"l": 10, "r": 10, "t": 25, "b": 10})
        st.plotly_chart(fig, width="stretch")
    with tabs[2]:
        vol = frame.dropna(subset=["rolling_vol_20"])
        fig = px.line(
            vol,
            x="date",
            y="rolling_vol_20",
            labels={"date": "日期", "rolling_vol_20": "年化波动率"},
        )
        fig.update_yaxes(tickformat=".1%")
        fig.update_layout(height=340, margin={"l": 10, "r": 10, "t": 25, "b": 10})
        st.plotly_chart(fig, width="stretch")

    if st.button("运行 GARCH 与 XGBoost", type="primary", width="stretch"):
        with st.spinner("按时间顺序 80%/20% 划分并进行真实测试集计算……"):
            st.session_state.model_result = get_model_result(
                data.end_date,
                frame,
                MODEL_RESULT_SCHEMA_VERSION,
            )
            st.session_state.simulation_result = None
            st.session_state.strategy_table = None
    result = st.session_state.get("model_result")
    if not model_result_is_current(result):
        clear_derived_results(st.session_state)
        st.warning("检测到旧版模型缓存，已安全清除；请重新运行模型。")
        return
    if result is None:
        st.info("点击按钮后才会拟合模型；页面不会显示预设准确率。")
        return
    xgb, garch = result.xgboost, result.garch
    state, percentile = _volatility_state(garch)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("下一交易日预测", f"{xgb.prediction_next_day:.4f}")
    m1.caption(f"{xgb.direction}｜较当前汇率 {xgb.prediction_next_day - xgb.previous_rate:+.4f}")
    m2.metric("MAE", f"{xgb.mae:.6f}")
    m3.metric("RMSE", f"{xgb.rmse:.6f}")
    m4.metric("方向准确率 DA", f"{xgb.direction_accuracy:.2%}")
    g1, g2, g3 = st.columns(3)
    g1.metric("GARCH 预测日波动率", f"{garch.daily_volatility:.4%}")
    g2.metric("GARCH 预测年化波动率", f"{garch.annual_volatility:.2%}")
    g3.metric("市场波动状态", state, f"历史百分位 {percentile:.1%}")
    st.caption(
        f"全量真实历史保留用于图表；模型统一使用最近窗口 {result.sample_start_date} 至 "
        f"{result.sample_end_date}（{result.sample_size} 个观测）。XGBoost 训练样本 "
        f"{xgb.train_size}、测试样本 {xgb.test_size}，按时间顺序划分；GARCH 使用同一窗口。"
    )
    if garch.annual_volatility >= 1.0:
        st.error(
            "GARCH 预测年化波动率达到或超过 100%。该值由当前建模窗口真实样本估计，"
            "请结合样本范围、异常行情与模型适用性复核后再用于教学结论。"
        )
    c1, c2 = st.columns(2)
    with c1:
        pred = pd.DataFrame(
            {
                "日期": pd.to_datetime(xgb.test_dates),
                "真实值": xgb.test_actual,
                "预测值": xgb.test_predicted,
            }
        )
        fig = go.Figure(
            [
                go.Scatter(x=pred["日期"], y=pred["真实值"], name="真实值"),
                go.Scatter(x=pred["日期"], y=pred["预测值"], name="预测值"),
            ]
        )
        fig.update_layout(
            title="测试集：真实值与预测值",
            height=350,
            margin={"l": 10, "r": 10, "t": 45, "b": 10},
        )
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = px.bar(
            xgb.feature_importance.sort_values("重要性"),
            x="重要性",
            y="特征",
            orientation="h",
            title="XGBoost 特征重要性",
        )
        fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 45, "b": 10})
        st.plotly_chart(fig, width="stretch")
