from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RiskMetrics:
    mean_income: float
    q05_income: float
    income_std: float
    var95: float
    cfar95: float
    risk_ratio: float
    risk_level: str


def validate_inputs(
    amount: float,
    term_days: int,
    budget_rate: float,
    spot_rate: float,
    forward_rate: float,
    hedge_ratio: float,
) -> None:
    errors: list[str] = []
    if amount <= 0:
        errors.append("外币金额 A 必须大于 0。")
    if int(term_days) <= 0:
        errors.append("结算期限 T 必须为正整数。")
    if budget_rate <= 0:
        errors.append("预算汇率 B 必须大于 0。")
    if spot_rate <= 0:
        errors.append("当前即期汇率 S₀ 必须大于 0。")
    if forward_rate <= 0:
        errors.append("远期汇率 F 必须大于 0。")
    if not 0 <= hedge_ratio <= 1:
        errors.append("套保比例 h 必须位于 0 至 1 之间。")
    if errors:
        raise ValueError("\n".join(errors))


def budget_income(amount: float, budget_rate: float) -> float:
    return float(amount * budget_rate)


def unhedged_income(amount: float, terminal_rate: np.ndarray | float) -> np.ndarray:
    return amount * np.asarray(terminal_rate, dtype=float)


def hedged_income(
    amount: float,
    hedge_ratio: float,
    forward_rate: float,
    terminal_rate: np.ndarray | float,
) -> np.ndarray:
    terminal = np.asarray(terminal_rate, dtype=float)
    return amount * (hedge_ratio * forward_rate + (1 - hedge_ratio) * terminal)


def hedge_effect(
    amount: float,
    hedge_ratio: float,
    forward_rate: float,
    terminal_rate: np.ndarray | float,
) -> np.ndarray:
    terminal = np.asarray(terminal_rate, dtype=float)
    return amount * hedge_ratio * (forward_rate - terminal)


def risk_level(risk_ratio: float) -> str:
    if risk_ratio < 0.02:
        return "低风险"
    if risk_ratio < 0.05:
        return "中风险"
    return "高风险"


def calculate_risk_metrics(incomes: np.ndarray, r_budget: float) -> RiskMetrics:
    values = np.asarray(incomes, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("人民币收入情景必须是一维、非空且全部为有限数值。")
    if r_budget <= 0:
        raise ValueError("预算人民币收入必须大于 0。")

    q05 = float(np.quantile(values, 0.05))
    losses = np.maximum(r_budget - values, 0.0)
    var95 = float(np.quantile(losses, 0.95))
    cfar95 = float(max(r_budget - q05, 0.0))
    ratio = cfar95 / r_budget
    return RiskMetrics(
        mean_income=float(np.mean(values)),
        q05_income=q05,
        income_std=float(np.std(values, ddof=0)),
        var95=var95,
        cfar95=cfar95,
        risk_ratio=ratio,
        risk_level=risk_level(ratio),
    )
