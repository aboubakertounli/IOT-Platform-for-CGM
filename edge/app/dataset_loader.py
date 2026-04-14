import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Common column name aliases found across PhysioNet CGM datasets.
# The loader tries each alias in order until it finds a match.
TIMESTAMP_ALIASES = ["timestamp", "Timestamp", "time", "Time", "date", "Date", "datetime", "DateTime"]
GLUCOSE_ALIASES = [
    "glucose",
    "Glucose",
    "glucose_mg_dl",
    "GlucoseValue",
    "Glucose Value",
    "glucose_value",
    "Historic Glucose mg/dL",
    "Scan Glucose mg/dL",
    "bg",
    "BG",
]


def _resolve_column(df: pd.DataFrame, configured_name: str, aliases: list[str]) -> str:
    """Return the actual column name present in the dataframe.

    Priority: configured name > aliases > first partial match.
    """
    if configured_name in df.columns:
        return configured_name

    for alias in aliases:
        if alias in df.columns:
            logger.info("Column '%s' not found, using alias '%s'", configured_name, alias)
            return alias

    # Last resort: case-insensitive partial match on 'gluc' or 'time'
    keyword = "gluc" if configured_name in GLUCOSE_ALIASES or "gluc" in configured_name.lower() else "time"
    for col in df.columns:
        if keyword in col.lower():
            logger.warning("Falling back to partial match column '%s' for '%s'", col, configured_name)
            return col

    raise ValueError(
        f"Cannot resolve column '{configured_name}'. "
        f"Available columns: {list(df.columns)}"
    )


def load_dataset(
    csv_path: str,
    col_timestamp: str = "timestamp",
    col_glucose: str = "glucose",
) -> list[dict]:
    """Load a CGM CSV file and return a clean list of {timestamp, glucose_mg_dl} dicts.

    Args:
        csv_path: Path to the CSV file.
        col_timestamp: Expected name for the timestamp column.
        col_glucose: Expected name for the glucose column.

    Returns:
        List of dicts sorted chronologically, with invalid rows removed.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path.resolve()}")

    df = pd.read_csv(path)
    logger.info("Loaded %d rows from %s (columns: %s)", len(df), csv_path, list(df.columns))

    ts_col = _resolve_column(df, col_timestamp, TIMESTAMP_ALIASES)
    gl_col = _resolve_column(df, col_glucose, GLUCOSE_ALIASES)

    df = df[[ts_col, gl_col]].copy()
    df.columns = ["timestamp", "glucose_mg_dl"]

    # Clean
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["glucose_mg_dl"] = pd.to_numeric(df["glucose_mg_dl"], errors="coerce")
    before = len(df)
    df = df.dropna()
    dropped = before - len(df)
    if dropped:
        logger.warning("Dropped %d invalid rows", dropped)

    df = df.sort_values("timestamp").reset_index(drop=True)
    logger.info("Dataset ready: %d valid readings", len(df))

    return df.to_dict(orient="records")
