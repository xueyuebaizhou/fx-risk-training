from __future__ import annotations

import pandas as pd
import streamlit as st

from .config import RANDOM_SEED, SIMULATION_PATHS
from .data import FXData, load_fx_data
from .models import ModelResult, fit_models
from .simulation import SimulationResult, simulate_fx_paths


@st.cache_data(ttl=6 * 60 * 60, show_spinner=False)
def get_fx_data() -> FXData:
    return load_fx_data()


@st.cache_resource(show_spinner=False)
def get_model_result(
    data_end_date: str,
    frame: pd.DataFrame,
    result_schema_version: int,
) -> ModelResult:
    # Both values are cache-key inputs. The explicit schema version prevents a
    # hot deployment from returning an object created by an older dataclass.
    del data_end_date, result_schema_version
    return fit_models(frame)


@st.cache_data(show_spinner=False)
def get_simulation_result(
    spot_rate: float,
    term_days: int,
    daily_drift: float,
    daily_volatility: float,
) -> SimulationResult:
    return simulate_fx_paths(
        spot_rate=spot_rate,
        term_days=term_days,
        daily_drift=daily_drift,
        daily_volatility=daily_volatility,
        n_paths=SIMULATION_PATHS,
        seed=RANDOM_SEED,
    )
