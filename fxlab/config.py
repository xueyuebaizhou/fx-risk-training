from pathlib import Path

APP_TITLE = "跨境汇率风险智能预警与避险策略实训工具"
PAIR = "USD/CNY"
UNIT = "CNY/USD"

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
REPORT_DIR = ROOT_DIR / "reports"
SNAPSHOT_PATH = DATA_DIR / "DEXCHUS_snapshot.csv"

FRED_SERIES = "DEXCHUS"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXCHUS"
FRED_PAGE = "https://fred.stlouisfed.org/series/DEXCHUS"
DATA_SOURCE = (
    "Board of Governors of the Federal Reserve System (US), "
    "DEXCHUS，经 FRED（Federal Reserve Bank of St. Louis）发布"
)

DEFAULT_AMOUNT = 1_000_000.0
DEFAULT_TERM_DAYS = 90
DEFAULT_BUDGET_RATE = 7.10
DEFAULT_FORWARD_RATE = 7.08
DEFAULT_HEDGE_RATIO = 0.50

MIN_USDCNY_RATE = 1.0
MAX_USDCNY_RATE = 20.0

TRADING_DAYS = 252
CALENDAR_DAYS = 365
SIMULATION_PATHS = 10_000
RANDOM_SEED = 20260831
QUICK_RATIOS = (0.0, 0.25, 0.5, 0.75, 1.0)

MIN_MODEL_ROWS = 260
MIN_GARCH_ROWS = 250
MODEL_LOOKBACK_YEARS = 5
