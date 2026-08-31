import numpy as np

from fxlab.models import build_features


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
