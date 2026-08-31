import streamlit as st

from fxlab.config import APP_TITLE
from fxlab.data import DataUnavailableError
from fxlab.pages import (
    case_page,
    exposure_page,
    model_page,
    report_page,
    simulation_page,
    strategy_page,
)
from fxlab.services import get_fx_data
from fxlab.state import initialise_state
from fxlab.ui import PAGES, inject_styles, sidebar_navigation

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()
initialise_state()

try:
    data = get_fx_data()
except DataUnavailableError as exc:
    st.error(str(exc))
    st.info(
        "系统不会用模拟或随机历史行情替代真实数据。请恢复网络或补充经核验的 FRED DEXCHUS 快照后重试。"
    )
    st.stop()

old_data_id = st.session_state.get("data_id")
new_data_id = f"{data.start_date}:{data.end_date}:{len(data.frame)}"
st.session_state.fx_data = data
st.session_state.spot_rate = data.spot
if old_data_id is not None and old_data_id != new_data_id:
    st.session_state.model_result = None
    st.session_state.simulation_result = None
    st.session_state.strategy_table = None
st.session_state.data_id = new_data_id

page = sidebar_navigation()
renderers = {
    PAGES[0]: case_page.render,
    PAGES[1]: model_page.render,
    PAGES[2]: exposure_page.render,
    PAGES[3]: strategy_page.render,
    PAGES[4]: simulation_page.render,
    PAGES[5]: report_page.render,
}
renderers[page]()
