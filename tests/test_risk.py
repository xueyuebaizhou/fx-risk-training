import numpy as np
import pytest

from fxlab.risk import (
    budget_income,
    calculate_risk_metrics,
    hedge_effect,
    hedged_income,
    risk_level,
    unhedged_income,
    validate_inputs,
)


def test_income_formulas():
    amount, budget, forward, terminal = 1_000_000, 7.10, 7.08, 6.95
    assert budget_income(amount, budget) == 7_100_000
    assert unhedged_income(amount, terminal) == pytest.approx(6_950_000)
    assert hedged_income(amount, 0.5, forward, terminal) == pytest.approx(7_015_000)
    assert hedge_effect(amount, 0.5, forward, terminal) == pytest.approx(65_000)


def test_var_cfar_use_same_income_scenarios():
    incomes = np.array([80, 90, 100, 110, 120], dtype=float)
    metrics = calculate_risk_metrics(incomes, 100, 110)
    assert metrics.q05_income == pytest.approx(np.quantile(incomes, 0.05))
    assert metrics.var95 == pytest.approx(max(np.quantile(110 - incomes, 0.95), 0))
    assert metrics.cfar95 == pytest.approx(max(100 - np.quantile(incomes, 0.05), 0))
    assert metrics.var95 != metrics.cfar95


def test_budget_changes_cfar_but_not_spot_referenced_var():
    incomes = np.array([80, 90, 100, 110, 120], dtype=float)
    first = calculate_risk_metrics(incomes, 100, 110)
    second = calculate_risk_metrics(incomes, 105, 110)
    assert first.var95 == second.var95
    assert first.cfar95 != second.cfar95


def test_risk_thresholds():
    assert risk_level(0.019999) == "低风险"
    assert risk_level(0.02) == "中风险"
    assert risk_level(0.049999) == "中风险"
    assert risk_level(0.05) == "高风险"


@pytest.mark.parametrize(
    "values",
    [
        (-1, 90, 7.1, 7.2, 7.08, 0.5),
        (1_000_000, 0, 7.1, 7.2, 7.08, 0.5),
        (1_000_000, 90, 0, 7.2, 7.08, 0.5),
        (1_000_000, 90, 7.1, 7.2, 0.0001, 0.5),
        (1_000_000, 90, 7.1, 7.2, 7.08, 1.1),
    ],
)
def test_invalid_inputs_are_rejected(values):
    with pytest.raises(ValueError):
        validate_inputs(*values)
