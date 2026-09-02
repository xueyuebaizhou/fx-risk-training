import tomllib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import plotly.graph_objects as go
import pytest
import streamlit as st

from fxlab.pages.model_page import _volatility_state
from fxlab.pages.simulation_page import _distribution_charts
from fxlab.ui import GRID, INK, PRIMARY, cny, inject_styles, risk_badge, style_chart


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
