import numpy as np
import pandas as pd

from fxlab.models import build_features, direction_label, select_recent_model_window


def test_features_only_use_current_or_past_data(real_frame):
    features = build_features(real_frame)
    assert (features["target_date"] > features["date"]).all()
    expected = (
        real_frame.set_index("date").loc[features["target_date"], "rate"].to_numpy()
    )
    assert np.allclose(features["target"].to_numpy(), expected)


def test_models_compute_real_metrics(fitted_models):
    xgb, garch = fitted_models.xgboost, fitted_models.garch
    assert xgb.train_size > xgb.test_size > 0
    assert xgb.mae >= 0 and xgb.rmse >= xgb.mae
    assert 0 <= xgb.direction_accuracy <= 1
    assert len(xgb.feature_importance) == 8
    assert garch.daily_volatility > 0
    assert garch.annual_volatility > garch.daily_volatility
    assert fitted_models.sample_size > xgb.train_size


def test_direction_label_matches_prediction_change():
    assert direction_label(7.09, 7.08) == "↑ 上涨"
    assert direction_label(7.07, 7.08) == "↓ 下跌"
    assert direction_label(7.08, 7.08) == "→ 持平"


def test_models_use_recent_window_while_history_can_remain_full(real_frame):
    old = real_frame.iloc[:20].copy()
    old["date"] = pd.date_range("1981-01-02", periods=len(old), freq="B")
    extended = pd.concat([old, real_frame], ignore_index=True)
    window = select_recent_model_window(extended)
    end = pd.Timestamp(window["date"].max())
    assert pd.Timestamp(window["date"].min()) >= end - pd.DateOffset(years=5)
    assert pd.Timestamp(extended["date"].min()).year == 1981
