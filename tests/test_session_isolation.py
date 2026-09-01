from fxlab.config import DEFAULT_FORWARD_RATE
from fxlab.pages.strategy_page import apply_quick_ratio
from fxlab.reporting import get_session_report_dir, remember_report
from fxlab.state import commit_widget_value, prepare_state, prepare_widget_value


def test_quick_ratio_updates_widget_and_business_state_together():
    state = {"_hedge_ratio_slider": 50, "hedge_ratio": 0.5}
    apply_quick_ratio(state, 75)
    assert state == {"_hedge_ratio_slider": 75, "hedge_ratio": 0.75}


def test_forward_rate_is_canonical_and_survives_widget_lifecycle():
    state = {"forward_rate": 0.0001}
    prepare_state(state)
    assert state["forward_rate"] == DEFAULT_FORWARD_RATE

    prepare_widget_value(state, "_forward_rate_input", "forward_rate")
    assert state["_forward_rate_input"] == DEFAULT_FORWARD_RATE
    state["_forward_rate_input"] = 7.12
    commit_widget_value(state, "_forward_rate_input", "forward_rate")
    del state["_forward_rate_input"]
    prepare_widget_value(state, "_forward_rate_input", "forward_rate")
    assert state["forward_rate"] == state["_forward_rate_input"] == 7.12


def test_report_history_and_directories_are_isolated_per_session(tmp_path):
    first, second = {}, {}
    first_dir = get_session_report_dir(first, tmp_path)
    second_dir = get_session_report_dir(second, tmp_path)
    assert first_dir != second_dir
    assert first_dir.parent == second_dir.parent == tmp_path

    remember_report(first, "first", b"pdf", "<html></html>")
    assert [item["name"] for item in first["generated_reports"]] == ["first"]
    assert "generated_reports" not in second
