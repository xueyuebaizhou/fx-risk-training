import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.service import _histogram, _risk_payload
from fxlab.risk import calculate_risk_metrics


def test_histogram_preserves_all_simulation_observations():
    values = np.linspace(6.7, 7.3, 10_000)

    histogram = _histogram(values, bins=40)

    assert len(histogram) == 40
    assert sum(bin_["count"] for bin_ in histogram) == 10_000
    assert all(set(bin_) == {"x", "count"} for bin_ in histogram)


def test_api_risk_payload_matches_core_business_metrics():
    metrics = calculate_risk_metrics(
        np.array([6_800_000.0, 7_000_000.0, 7_200_000.0]),
        r_budget=7_100_000.0,
        spot_reference_income=7_000_000.0,
    )

    payload = _risk_payload(metrics)

    assert payload["meanIncome"] == 7_000_000.0
    assert payload["riskLevel"] == metrics.risk_level
    assert payload["cfar95"] == round(metrics.cfar95, 2)


def test_report_endpoint_accepts_the_frontend_payload(monkeypatch):
    captured = {}

    def fake_build_report(request):
        captured["request"] = request
        return b"%PDF-test", "application/pdf", "fx-training-report.pdf"

    monkeypatch.setattr("backend.main.build_report", fake_build_report)
    response = TestClient(app).post(
        "/api/v1/reports",
        json={
            "amount": 5_000_000,
            "term_days": 90,
            "budget_rate": 7.1,
            "forward_rate": 7.08,
            "hedge_ratio": 0.6,
            "final_ratio": 0.6,
            "decision_reason": "兼顾预算确定性与部分汇率改善空间。",
            "format": "pdf",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert captured["request"].term_days == 90
    assert captured["request"].decision_reason.startswith("兼顾预算")
