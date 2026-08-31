from fxlab.pages.strategy_page import apply_quick_ratio
from fxlab.reporting import get_session_report_dir, remember_report


def test_quick_ratio_updates_widget_and_business_state_together():
    state = {"hedge_ratio_slider": 50, "hedge_ratio": 0.5}
    apply_quick_ratio(state, 75)
    assert state == {"hedge_ratio_slider": 75, "hedge_ratio": 0.75}


def test_report_history_and_directories_are_isolated_per_session(tmp_path):
    first, second = {}, {}
    first_dir = get_session_report_dir(first, tmp_path)
    second_dir = get_session_report_dir(second, tmp_path)
    assert first_dir != second_dir
    assert first_dir.parent == second_dir.parent == tmp_path

    remember_report(first, "first", b"pdf", "<html></html>")
    assert [item["name"] for item in first["generated_reports"]] == ["first"]
    assert "generated_reports" not in second
