from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import (
    CALENDAR_DAYS,
    QUICK_RATIOS,
    RANDOM_SEED,
    SIMULATION_PATHS,
    TRADING_DAYS,
)
from .risk import budget_income, calculate_risk_metrics, hedged_income


@dataclass(frozen=True)
class SimulationResult:
    paths: np.ndarray
    terminal_rates: np.ndarray
    trading_days: int
    daily_drift: float
    daily_volatility: float
    seed: int


def calendar_to_trading_days(term_days: int) -> int:
    if int(term_days) <= 0:
        raise ValueError("结算期限必须为正整数。")
    return max(1, round(int(term_days) * TRADING_DAYS / CALENDAR_DAYS))


def simulate_fx_paths(
    spot_rate: float,
    term_days: int,
    daily_drift: float,
    daily_volatility: float,
    n_paths: int = SIMULATION_PATHS,
    seed: int = RANDOM_SEED,
) -> SimulationResult:
    if spot_rate <= 0:
        raise ValueError("起始即期汇率必须大于 0。")
    if daily_volatility <= 0 or not np.isfinite(daily_volatility):
        raise ValueError("GARCH 日波动率必须为正的有限数值。")
    if n_paths != SIMULATION_PATHS:
        raise ValueError(f"完整计算必须使用 {SIMULATION_PATHS:,} 条路径。")

    steps = calendar_to_trading_days(term_days)
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal((n_paths, steps))
    log_steps = (daily_drift - 0.5 * daily_volatility**2) + daily_volatility * shocks
    paths = spot_rate * np.exp(np.cumsum(log_steps, axis=1))
    return SimulationResult(
        paths=paths,
        terminal_rates=paths[:, -1],
        trading_days=steps,
        daily_drift=float(daily_drift),
        daily_volatility=float(daily_volatility),
        seed=seed,
    )


def compare_hedge_strategies(
    terminal_rates: np.ndarray,
    amount: float,
    budget_rate: float,
    forward_rate: float,
    ratios: tuple[float, ...] = QUICK_RATIOS,
) -> pd.DataFrame:
    r_budget = budget_income(amount, budget_rate)
    baseline = calculate_risk_metrics(
        hedged_income(amount, 0.0, forward_rate, terminal_rates), r_budget
    )
    rows: list[dict[str, float | str]] = []
    for ratio in ratios:
        incomes = hedged_income(amount, ratio, forward_rate, terminal_rates)
        metrics = calculate_risk_metrics(incomes, r_budget)
        reduction = (
            (baseline.cfar95 - metrics.cfar95) / baseline.cfar95
            if baseline.cfar95 > 0
            else 0.0
        )
        rows.append(
            {
                "套保比例": ratio,
                "平均收入": metrics.mean_income,
                "5%分位数收入": metrics.q05_income,
                "收入标准差": metrics.income_std,
                "VaR95": metrics.var95,
                "CFaR95": metrics.cfar95,
                "Risk Ratio": metrics.risk_ratio,
                "风险等级": metrics.risk_level,
                "风险下降幅度": reduction,
            }
        )
    return pd.DataFrame(rows)
