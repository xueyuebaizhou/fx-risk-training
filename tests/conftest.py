from pathlib import Path

import pandas as pd
import pytest

from fxlab.data import _normalise
from fxlab.models import fit_models


@pytest.fixture(scope="session")
def real_frame():
    path = Path(__file__).resolve().parents[1] / "data" / "DEXCHUS_snapshot.csv"
    return _normalise(pd.read_csv(path))


@pytest.fixture(scope="session")
def fitted_models(real_frame):
    return fit_models(real_frame)
