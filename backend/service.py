from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from fxlab.config import MODEL_RESULT_SCHEMA_VERSION, SIMULATION_PATHS
from fxlab.data import FXData, load_fx_data
from fxlab.models import ModelResult, fit_models
from fxlab.reporting import build_html_report, build_pdf_report
from fxlab.risk import budget_income, calculate_risk_metrics, hedge_effect, hedged_income
from fxlab.simulation import SimulationResult, compare_hedge_strategies, simulate_fx_paths

from .schemas import ReportRequest, ScenarioInput


@lru_cache(maxsize=1)
def get_fx_data() -> FXData:
    return load_fx_data()


@lru_cache(maxsize=2)
def get_models(data_end_date: str, schema_version: int) -> ModelResult:
    del data_end_date, schema_version
    return fit_models(get_fx_data().frame)


def _number(value: float, digits: int = 8) -> float:
    return round(float(value), digits)


def _date(value: Any) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _series(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        log_return = row.log_return
        rolling_vol = row.rolling_vol_20
        rows.append(
            {
                "date": _date(row.date),
                "rate": _number(row.rate, 6),
                "returnPct": None if pd.isna(log_return) else _number(log_return * 100, 6),
                "volatilityPct": (
                    None if pd.isna(rolling_vol) else _number(rolling_vol * 100, 6)
                ),
            }
        )
    return rows


def market_payload(data: FXData) -> dict[str, Any]:
    return {
        "pair": "USD/CNY",
        "unit": "CNY/USD",
        "spotRate": _number(data.spot, 6),
        "source": data.source,
        "sourceUrl": data.source_url,
        "retrievedAt": data.retrieved_at,
        "mode": data.mode,
        "startDate": data.start_date,
        "endDate": data.end_date,
        "observations": len(data.frame),
        "series": _series(data.frame),
    }


def _risk_payload(metrics) -> dict[str, Any]:
    return {
        "meanIncome": _number(metrics.mean_income, 2),
        "q05Income": _number(metrics.q05_income, 2),
        "incomeStd": _number(metrics.income_std, 2),
        "var95": _number(metrics.var95, 2),
        "cfar95": _number(metrics.cfar95, 2),
        "riskRatio": _number(metrics.risk_ratio, 8),
        "riskLevel": metrics.risk_level,
    }


def _histogram(values: np.ndarray, bins: int = 44) -> list[dict[str, Any]]:
    counts, edges = np.histogram(np.asarray(values, dtype=float), bins=bins)
    return [
        {
            "x": _number((edges[index] + edges[index + 1]) / 2, 6),
            "count": int(count),
        }
        for index, count in enumerate(counts)
    ]


def _volatility_state(models: ModelResult) -> tuple[str, float]:
    history = np.asarray(models.garch.conditional_volatility, dtype=float)
    percentile = float(np.mean(history <= models.garch.daily_volatility))
    if percentile < 1 / 3:
        return "低", percentile
    if percentile < 2 / 3:
        return "中", percentile
    return "高", percentile


def _simulation(params: ScenarioInput, models: ModelResult, spot_rate: float) -> SimulationResult:
    return simulate_fx_paths(
        spot_rate=spot_rate,
        term_days=params.term_days,
        daily_drift=models.garch.daily_drift,
        daily_volatility=models.garch.daily_volatility,
        n_paths=SIMULATION_PATHS,
    )


def analysis_payload(params: ScenarioInput) -> tuple[dict[str, Any], dict[str, Any]]:
    data = get_fx_data()
    models = get_models(data.end_date, MODEL_RESULT_SCHEMA_VERSION)
    simulation = _simulation(params, models, data.spot)
    terminal_rates = simulation.terminal_rates
    budget = budget_income(params.amount, params.budget_rate)
    spot_income = params.amount * data.spot

    unhedged_incomes = hedged_income(
        params.amount,
        0,
        params.forward_rate,
        terminal_rates,
    )
    selected_incomes = hedged_income(
        params.amount,
        params.hedge_ratio,
        params.forward_rate,
        terminal_rates,
    )
    unhedged = calculate_risk_metrics(unhedged_incomes, budget, spot_income)
    selected = calculate_risk_metrics(selected_incomes, budget, spot_income)
    cfar_reduction = (
        (unhedged.cfar95 - selected.cfar95) / unhedged.cfar95
        if unhedged.cfar95
        else 0.0
    )
    strategies = compare_hedge_strategies(
        terminal_rates,
        params.amount,
        params.budget_rate,
        data.spot,
        params.forward_rate,
    )
    market_state, percentile = _volatility_state(models)

    test_dates = [_date(value) for value in models.xgboost.test_dates]
    test_series = [
        {
            "date": date,
            "actual": _number(actual, 6),
            "predicted": _number(predicted, 6),
        }
        for date, actual, predicted in zip(
            test_dates,
            models.xgboost.test_actual,
            models.xgboost.test_predicted,
            strict=True,
        )
    ]
    conditional = [
        {"date": _date(date), "volatilityPct": _number(vol * 100, 6)}
        for date, vol in zip(
            models.garch.volatility_dates,
            models.garch.conditional_volatility,
            strict=True,
        )
    ]
    sample_count = min(48, len(simulation.paths))
    paths = [
        {
            "id": index + 1,
            "values": [_number(data.spot, 6)]
            + [_number(value, 6) for value in simulation.paths[index]],
        }
        for index in range(sample_count)
    ]

    strategy_rows: list[dict[str, Any]] = []
    for row in strategies.to_dict(orient="records"):
        strategy_rows.append(
            {
                "ratio": _number(row["套保比例"], 4),
                "meanIncome": _number(row["平均收入"], 2),
                "q05Income": _number(row["5%分位数收入"], 2),
                "incomeStd": _number(row["收入标准差"], 2),
                "var95": _number(row["VaR95"], 2),
                "cfar95": _number(row["CFaR95"], 2),
                "riskRatio": _number(row["Risk Ratio"], 8),
                "riskLevel": row["风险等级"],
                "riskReduction": _number(row["风险下降幅度"], 8),
            }
        )

    payload = {
        "inputs": {
            "amount": params.amount,
            "termDays": params.term_days,
            "budgetRate": params.budget_rate,
            "forwardRate": params.forward_rate,
            "hedgeRatio": params.hedge_ratio,
            "spotRate": _number(data.spot, 6),
        },
        "model": {
            "predictionNextDay": _number(models.xgboost.prediction_next_day, 6),
            "previousRate": _number(models.xgboost.previous_rate, 6),
            "direction": models.xgboost.direction,
            "mae": _number(models.xgboost.mae, 8),
            "rmse": _number(models.xgboost.rmse, 8),
            "directionAccuracy": _number(models.xgboost.direction_accuracy, 8),
            "dailyVolatility": _number(models.garch.daily_volatility, 8),
            "annualVolatility": _number(models.garch.annual_volatility, 8),
            "dailyDrift": _number(models.garch.daily_drift, 10),
            "marketState": market_state,
            "volatilityPercentile": _number(percentile, 8),
            "sampleStartDate": models.sample_start_date,
            "sampleEndDate": models.sample_end_date,
            "sampleSize": models.sample_size,
            "trainSize": models.xgboost.train_size,
            "testSize": models.xgboost.test_size,
            "featureImportance": [
                {"feature": row["特征"], "importance": _number(row["重要性"], 8)}
                for row in models.xgboost.feature_importance.to_dict(orient="records")
            ],
            "testSeries": test_series,
            "conditionalVolatility": conditional,
        },
        "exposure": {
            "direction": "美元应收",
            "budgetIncome": _number(budget, 2),
            "spotReferenceIncome": _number(spot_income, 2),
            "unhedged": _risk_payload(unhedged),
        },
        "strategy": {
            "lockedAmount": _number(params.amount * params.hedge_ratio, 2),
            "selected": _risk_payload(selected),
            "cfarReduction": _number(cfar_reduction, 8),
            "meanHedgeEffect": _number(
                hedge_effect(
                    params.amount,
                    params.hedge_ratio,
                    params.forward_rate,
                    float(np.mean(terminal_rates)),
                ),
                2,
            ),
        },
        "simulation": {
            "pathsCount": SIMULATION_PATHS,
            "displayPathsCount": sample_count,
            "tradingDays": simulation.trading_days,
            "seed": simulation.seed,
            "terminalMean": _number(np.mean(terminal_rates), 6),
            "terminalQ05": _number(np.quantile(terminal_rates, 0.05), 6),
            "paths": paths,
            "terminalRates": [_number(value, 6) for value in terminal_rates],
            "terminalHistogram": _histogram(terminal_rates),
            "incomeHistogram": _histogram(selected_incomes / 10_000),
        },
        "strategies": strategy_rows,
    }
    report_state = {
        "fx_data": data,
        "model_result": models,
        "simulation_result": simulation,
        "strategy_table": strategies,
        "amount": params.amount,
        "term_days": params.term_days,
        "spot_rate": data.spot,
        "budget_rate": params.budget_rate,
        "forward_rate": params.forward_rate,
    }
    return payload, report_state


def build_report(request: ReportRequest) -> tuple[bytes, str, str]:
    params = ScenarioInput(
        amount=request.amount,
        term_days=request.term_days,
        budget_rate=request.budget_rate,
        forward_rate=request.forward_rate,
        hedge_ratio=request.hedge_ratio,
    )
    _, state = analysis_payload(params)
    state.update(
        {
            "final_ratio": request.final_ratio,
            "decision_reason": request.decision_reason,
        }
    )
    if request.format == "html":
        content = build_html_report(state).encode("utf-8")
        return content, "text/html; charset=utf-8", "fx-training-report.html"
    return build_pdf_report(state), "application/pdf", "fx-training-report.pdf"
