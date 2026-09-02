import tomllib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
import streamlit as st

from fxlab.pages.model_page import _history_line_chart, _volatility_state
from fxlab.pages.simulation_page import DISPLAY_PATHS, _distribution_charts, _path_scenario_chart
from fxlab.ui import (
    CHART_PALETTE,
    GRID,
    INK,
    PRIMARY,
    cny,
    inject_styles,
    risk_badge,
    style_chart,
)


@pytest.mark.parametrize(
    ("daily_volatility", "expected_state", "expected_percentile"),
    [
        (1.0, "低", 0.25),
        (2.0, "中", 0.5),
        (4.0, "高", 1.0),
    ],
)
def test_market_volatility_state_is_distinct_from_exposure_risk(
    daily_volatility,
    expected_state,
    expected_percentile,
):
    result = SimpleNamespace(
        conditional_volatility=np.array([1.0, 2.0, 3.0, 4.0]),
        daily_volatility=daily_volatility,
    )

    state, percentile = _volatility_state(result)

    assert state == expected_state
    assert percentile == expected_percentile


def test_negative_currency_places_minus_before_currency_symbol():
    assert cny(-361_900) == "-¥36.19 万"
    assert cny(361_900) == "¥36.19 万"


def test_exposure_badge_uses_explicit_business_risk_label(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        st,
        "markdown",
        lambda body, unsafe_allow_html: rendered.append((body, unsafe_allow_html)),
    )

    risk_badge("高风险")

    assert "企业敞口风险" in rendered[0][0]
    assert "高风险" in rendered[0][0]
    assert rendered[0][1] is True


def test_distribution_charts_use_chinese_axes_and_reference_lines():
    terminal_rates = np.array([6.8, 6.9, 7.0, 7.1, 7.2])
    incomes = terminal_rates * 1_000_000

    rate_fig, income_fig = _distribution_charts(terminal_rates, incomes, 0.0)

    assert rate_fig.layout.yaxis.title.text == "模拟次数"
    assert income_fig.layout.yaxis.title.text == "模拟次数"
    assert len(rate_fig.layout.shapes) == 1
    assert rate_fig.layout.shapes[0].x0 == pytest.approx(terminal_rates.mean())
    assert len(income_fig.layout.shapes) == 2
    assert income_fig.layout.shapes[0].x0 == pytest.approx(incomes.mean() / 10_000)
    assert income_fig.layout.shapes[1].x0 == pytest.approx(np.quantile(incomes / 10_000, 0.05))
    assert [annotation.text for annotation in rate_fig.layout.annotations] == ["均值 7.0000"]
    assert [annotation.text for annotation in income_fig.layout.annotations] == [
        "均值 700.00 万元",
        "5%分位 682.00 万元",
    ]


def test_fixed_income_distribution_merges_identical_reference_lines():
    terminal_rates = np.array([6.8, 6.9, 7.0])
    incomes = np.full(terminal_rates.shape, 7_080_000.0)

    _, income_fig = _distribution_charts(terminal_rates, incomes, 1.0)

    assert len(income_fig.layout.shapes) == 1
    assert income_fig.layout.annotations[0].text == "均值 = 5%分位 708.00 万元"


def test_chart_theme_changes_presentation_without_changing_data():
    figure = style_chart(go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])]))

    assert list(figure.data[0].x) == [1, 2]
    assert list(figure.data[0].y) == [3, 4]
    assert figure.data[0].line.color == PRIMARY
    assert figure.layout.font.color == INK
    assert figure.layout.yaxis.gridcolor == GRID
    assert figure.layout.paper_bgcolor == "#FFFFFF"
    assert "title" not in figure.to_plotly_json()["layout"]


def test_chart_theme_styles_only_real_titles():
    figure = go.Figure(data=[go.Bar(x=["A"], y=[1])])
    figure.update_layout(title_text="真实标题")

    styled = style_chart(figure)

    assert styled.layout.title.text == "真实标题"
    assert styled.layout.title.font.color == INK


def test_chart_theme_also_styles_webgl_history_lines():
    figure = style_chart(go.Figure(data=[go.Scattergl(x=[1, 2], y=[3, 4])]))

    assert figure.data[0].line.color == PRIMARY
    assert figure.data[0].line.width == pytest.approx(1.8)


def test_history_chart_uses_webgl_only_for_long_series():
    short = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=20), "rate": 6.8})
    long = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=1_500), "rate": 6.8})

    short_chart = _history_line_chart(short, "rate", {"date": "日期"})
    long_chart = _history_line_chart(long, "rate", {"date": "日期"})

    assert short_chart.data[0].type == "scatter"
    assert long_chart.data[0].type == "scattergl"


def test_path_scenario_chart_uses_full_product_palette():
    paths = np.tile(np.linspace(6.7, 6.9, 12), (DISPLAY_PATHS, 1))

    figure = _path_scenario_chart(paths, 6.8)

    assert len(figure.data) == DISPLAY_PATHS
    assert {trace.line.color for trace in figure.data} == set(CHART_PALETTE)
    assert all(trace.opacity == pytest.approx(0.24) for trace in figure.data)
    assert all(trace.showlegend is False for trace in figure.data)
    assert f"{DISPLAY_PATHS} 条路径" in figure.layout.title.text
    assert "10,000 条" in figure.layout.title.text


def test_sidebar_navigation_keeps_radio_inputs_accessible(monkeypatch):
    rendered = []
    monkeypatch.setattr(
        st,
        "markdown",
        lambda body, unsafe_allow_html: rendered.append((body, unsafe_allow_html)),
    )

    inject_styles()

    stylesheet = rendered[0][0]
    assert 'label[data-baseweb="radio"] > div:first-child' not in stylesheet
    assert '[data-testid="stRadioOption"][data-selected="true"]' in stylesheet
    assert '[data-testid="stNumberInputContainer"]' in stylesheet
    assert '[data-testid="stToolbarActions"]' in stylesheet
    assert rendered[0][1] is True


def test_streamlit_theme_matches_shared_product_palette():
    config_path = Path(__file__).parents[1] / ".streamlit" / "config.toml"
    with config_path.open("rb") as config_file:
        config = tomllib.load(config_file)

    assert config["client"]["toolbarMode"] == "minimal"
    assert config["theme"]["primaryColor"] == PRIMARY
    assert config["theme"]["backgroundColor"] == "#F8F7FB"
    assert config["theme"]["secondaryBackgroundColor"] == "#FFFFFF"
