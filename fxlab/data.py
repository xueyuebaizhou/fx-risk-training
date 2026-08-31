from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .config import (
    DATA_SOURCE,
    FRED_PAGE,
    FRED_URL,
    MIN_MODEL_ROWS,
    SNAPSHOT_PATH,
    TRADING_DAYS,
)


class DataUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class FXData:
    frame: pd.DataFrame
    source: str
    source_url: str
    retrieved_at: str
    mode: str

    @property
    def start_date(self) -> str:
        return self.frame["date"].min().strftime("%Y-%m-%d")

    @property
    def end_date(self) -> str:
        return self.frame["date"].max().strftime("%Y-%m-%d")

    @property
    def spot(self) -> float:
        return float(self.frame["rate"].iloc[-1])


def _normalise(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty or len(raw.columns) < 2:
        raise DataUnavailableError("数据文件为空或缺少日期、汇率字段。")
    date_col = next(
        (c for c in raw.columns if c.lower() in {"date", "observation_date"}),
        raw.columns[0],
    )
    value_col = next((c for c in raw.columns if c.upper() == "DEXCHUS"), raw.columns[1])
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(raw[date_col], errors="coerce"),
            "rate": pd.to_numeric(raw[value_col], errors="coerce"),
        }
    ).dropna()
    frame = (
        frame.drop_duplicates("date", keep="last")
        .sort_values("date")
        .reset_index(drop=True)
    )
    frame = frame[(frame["rate"] > 0) & np.isfinite(frame["rate"])]
    if len(frame) < MIN_MODEL_ROWS:
        raise DataUnavailableError(
            f"有效数据仅 {len(frame)} 行，少于建模最低要求 {MIN_MODEL_ROWS} 行。"
        )
    frame["log_return"] = np.log(frame["rate"] / frame["rate"].shift(1))
    frame["rolling_vol_20"] = frame["log_return"].rolling(20).std() * np.sqrt(
        TRADING_DAYS
    )
    return frame


def _read_snapshot(path: Path) -> FXData:
    if not path.exists():
        raise DataUnavailableError("实时下载失败，且仓库中不存在已核验的真实数据快照。")
    frame = _normalise(pd.read_csv(path))
    retrieved = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )
    return FXData(frame, DATA_SOURCE, FRED_PAGE, retrieved, "已核验真实快照")


def load_fx_data(timeout: int = 15, snapshot_path: Path = SNAPSHOT_PATH) -> FXData:
    try:
        response = requests.get(FRED_URL, timeout=timeout)
        response.raise_for_status()
        raw = pd.read_csv(pd.io.common.StringIO(response.text))
        frame = _normalise(raw)
        retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return FXData(frame, DATA_SOURCE, FRED_PAGE, retrieved, "FRED 在线真实数据")
    except (
        DataUnavailableError,
        KeyError,
        OSError,
        ValueError,
        requests.RequestException,
        pd.errors.ParserError,
    ) as live_error:
        try:
            return _read_snapshot(snapshot_path)
        except Exception as snapshot_error:
            raise DataUnavailableError(
                "USD/CNY 真实数据不可用，系统已停止计算。"
                f" 在线错误：{live_error}；快照错误：{snapshot_error}"
            ) from snapshot_error
