from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from .config import MIN_GARCH_ROWS, MIN_MODEL_ROWS, TRADING_DAYS

FEATURE_LABELS = {
    "rate": "当前汇率",
    "lag_return_1": "滞后1日收益率",
    "return_5": "5日收益率",
    "return_20": "20日收益率",
    "volatility_20": "20日滚动波动率",
    "ma_5": "5日移动平均",
    "ma_20": "20日移动平均",
    "ma_ratio": "短长均线比",
}


@dataclass(frozen=True)
class XGBoostResult:
    prediction_next_day: float
    previous_rate: float
    direction: str
    mae: float
    rmse: float
    direction_accuracy: float
    feature_importance: pd.DataFrame
    test_actual: np.ndarray
    test_predicted: np.ndarray
    test_dates: np.ndarray
    train_size: int
    test_size: int


@dataclass(frozen=True)
class GARCHResult:
    daily_volatility: float
    annual_volatility: float
    daily_drift: float
    conditional_volatility: np.ndarray
    volatility_dates: np.ndarray


@dataclass(frozen=True)
class ModelResult:
    xgboost: XGBoostResult
    garch: GARCHResult


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame[["date", "rate"]].copy().sort_values("date")
    log_return = np.log(df["rate"] / df["rate"].shift(1))
    df["lag_return_1"] = log_return
    df["return_5"] = np.log(df["rate"] / df["rate"].shift(5))
    df["return_20"] = np.log(df["rate"] / df["rate"].shift(20))
    df["volatility_20"] = log_return.rolling(20).std()
    df["ma_5"] = df["rate"].rolling(5).mean()
    df["ma_20"] = df["rate"].rolling(20).mean()
    df["ma_ratio"] = df["ma_5"] / df["ma_20"] - 1
    df["target"] = df["rate"].shift(-1)
    df["target_date"] = df["date"].shift(-1)
    return df.dropna().reset_index(drop=True)


def fit_xgboost(frame: pd.DataFrame) -> XGBoostResult:
    features = build_features(frame)
    if len(features) < MIN_MODEL_ROWS:
        raise ValueError(f"特征样本仅 {len(features)} 行，无法可靠划分训练集和测试集。")
    columns = list(FEATURE_LABELS)
    split = int(len(features) * 0.8)
    train, test = features.iloc[:split], features.iloc[split:]
    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=320,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=20260831,
        n_jobs=1,
    )
    model.fit(train[columns], train["target"])
    predicted = model.predict(test[columns])
    actual = test["target"].to_numpy(dtype=float)
    previous = test["rate"].to_numpy(dtype=float)
    actual_direction = np.sign(actual - previous)
    predicted_direction = np.sign(predicted - previous)
    direction_accuracy = float(np.mean(actual_direction == predicted_direction))

    latest_all = build_features_with_latest(frame)
    latest_row = latest_all.iloc[[-1]]
    next_prediction = float(model.predict(latest_row[columns])[0])
    latest_rate = float(latest_row["rate"].iloc[0])
    importance = pd.DataFrame(
        {
            "特征": [FEATURE_LABELS[c] for c in columns],
            "重要性": model.feature_importances_,
        }
    ).sort_values("重要性", ascending=False)
    return XGBoostResult(
        prediction_next_day=next_prediction,
        previous_rate=latest_rate,
        direction="上涨"
        if next_prediction > latest_rate
        else "下跌"
        if next_prediction < latest_rate
        else "持平",
        mae=float(mean_absolute_error(actual, predicted)),
        rmse=float(mean_squared_error(actual, predicted) ** 0.5),
        direction_accuracy=direction_accuracy,
        feature_importance=importance.reset_index(drop=True),
        test_actual=actual,
        test_predicted=np.asarray(predicted, dtype=float),
        test_dates=test["target_date"].to_numpy(),
        train_size=len(train),
        test_size=len(test),
    )


def build_features_with_latest(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame[["date", "rate"]].copy().sort_values("date")
    log_return = np.log(df["rate"] / df["rate"].shift(1))
    df["lag_return_1"] = log_return
    df["return_5"] = np.log(df["rate"] / df["rate"].shift(5))
    df["return_20"] = np.log(df["rate"] / df["rate"].shift(20))
    df["volatility_20"] = log_return.rolling(20).std()
    df["ma_5"] = df["rate"].rolling(5).mean()
    df["ma_20"] = df["rate"].rolling(20).mean()
    df["ma_ratio"] = df["ma_5"] / df["ma_20"] - 1
    return df.dropna().reset_index(drop=True)


def fit_garch(frame: pd.DataFrame) -> GARCHResult:
    returns = np.log(frame["rate"] / frame["rate"].shift(1)).dropna()
    if len(returns) < MIN_GARCH_ROWS:
        raise ValueError(f"收益率样本仅 {len(returns)} 行，少于 GARCH 最低要求。")
    returns_pct = returns * 100.0
    fitted = arch_model(
        returns_pct,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="normal",
        rescale=False,
    ).fit(disp="off", show_warning=False)
    forecast_variance = float(
        fitted.forecast(horizon=1, reindex=False).variance.iloc[-1, 0]
    )
    daily_volatility = np.sqrt(forecast_variance) / 100.0
    conditional = np.asarray(fitted.conditional_volatility, dtype=float) / 100.0
    return GARCHResult(
        daily_volatility=float(daily_volatility),
        annual_volatility=float(daily_volatility * np.sqrt(TRADING_DAYS)),
        daily_drift=float(returns.mean()),
        conditional_volatility=conditional,
        volatility_dates=frame["date"].iloc[-len(conditional) :].to_numpy(),
    )


def fit_models(frame: pd.DataFrame) -> ModelResult:
    return ModelResult(xgboost=fit_xgboost(frame), garch=fit_garch(frame))
