import numpy as np

from fxlab.config import RANDOM_SEED, SIMULATION_PATHS
from fxlab.simulation import (
    calendar_to_trading_days,
    compare_hedge_strategies,
    simulate_fx_paths,
)


def test_calendar_day_conversion_is_unified():
    assert calendar_to_trading_days(90) == 62
    assert calendar_to_trading_days(30) == 21


def test_ten_thousand_paths_are_reproducible(fitted_models, real_frame):
    kwargs = {
        "spot_rate": float(real_frame["rate"].iloc[-1]),
        "term_days": 90,
        "daily_drift": fitted_models.garch.daily_drift,
        "daily_volatility": fitted_models.garch.daily_volatility,
    }
    first = simulate_fx_paths(**kwargs)
    second = simulate_fx_paths(**kwargs)
    assert first.paths.shape == (SIMULATION_PATHS, 62)
    assert first.seed == RANDOM_SEED
    assert np.array_equal(first.terminal_rates, second.terminal_rates)
    assert (first.terminal_rates > 0).all()


def test_strategy_table_uses_one_terminal_sample(fitted_models, real_frame):
    sim = simulate_fx_paths(
        float(real_frame["rate"].iloc[-1]),
        90,
        fitted_models.garch.daily_drift,
        fitted_models.garch.daily_volatility,
    )
    table = compare_hedge_strategies(sim.terminal_rates, 1_000_000, 7.10, 7.08)
    assert table["套保比例"].tolist() == [0, 0.25, 0.5, 0.75, 1]
    assert table["收入标准差"].is_monotonic_decreasing
    assert table.iloc[-1]["收入标准差"] < 1e-6
