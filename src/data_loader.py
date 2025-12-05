""""
Data Loader
CSV formats:
1. prices.csv: columns = [month, coal, gas, oil]
2. storage.csv: columns = [fuel, capacity]
3. plant_capacity.csv: columns = [fuel, capacity]
4. demand.csv: columns = [month, demand]
"""

import pandas as pd
import numpy as np
from typing import Optional, Union

def load_prices(
    file_path: str,
    start: Optional[Union[str, pd.Timestamp]] = None,
    end:   Optional[Union[str, pd.Timestamp]] = None,
    resample_method: str = "ME"
) -> pd.DataFrame:
    """
    Load fuel prices from CSV, parse dates, limit to [start, end], and resample.

    Parameters
    ----------
    file_path : str
        Path to CSV. The function expects the first column to be the date (or a 'month' column).
    start, end : str or pd.Timestamp, optional
        Inclusive date range to select. If None uses full available range.
    resample_method : str, default "ME"
        A pandas offset alias for resampling (e.g. "M" monthly, "MS" month-start,
        "W" weekly, "D" daily, "Q" quarterly, etc.).

    Returns
    -------
    pd.DataFrame
        Resampled DataFrame indexed by datetime (period end for rules like "M").
    """
    # Read CSV, parse the first column as dates
    df = pd.read_csv(file_path, parse_dates=[0])
    if df.shape[1] < 2:
        raise ValueError("CSV must contain a date column plus at least the fuel columns.")

    # Use the first column as the datetime index
    date_col = df.columns[0]
    df = df.set_index(date_col)
    df.index = pd.to_datetime(df.index)  # ensure datetime index

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Required columns
    required = {"coal", "gas", "oil"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}. Available: {list(df.columns)}")

    # Coerce all columns to numeric (non-numeric -> NaN), keep optional 'lignite' automatically
    df = df.apply(pd.to_numeric, errors="coerce")

    # Determine start/end bounds
    if start is not None:
        start_ts = pd.to_datetime(start)
    else:
        start_ts = df.index.min()

    if end is not None:
        # Set end to the end of the month at 23:00 to include full month data
        end_ts = pd.to_datetime(end) + pd.offsets.MonthEnd(1) + pd.offsets.Hour(23)
    else:
        end_ts = df.index.max()

    if start_ts > end_ts:
        raise ValueError("`start` must be less than or equal to `end`.")

    # Select the requested time window (inclusive)
    df = df.loc[start_ts:end_ts]
    if df.empty:
        raise ValueError("No data in the selected date range.")

    # Resample & aggregate (default: mean)
    df = df.resample(resample_method).mean()

    return df

def load_storage(file_path: str) -> dict:
    """Load storage capacities from CSV and return as dictionary."""
    df = pd.read_csv(file_path)
    required_cols = {"fuel", "capacity"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"storage.csv must contain columns: {required_cols}")
    return dict(zip(df["fuel"], df["capacity"]))

def load_efficiency(file_path: str) -> dict:
    """Load efficiency rates from CSV and return as dictionary."""
    df = pd.read_csv(file_path)
    required_cols = {"fuel", "efficiency"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"efficiency.csv must contain columns: {required_cols}")
    return dict(zip(df["fuel"], df["efficiency"]))

def load_plant_capacity(file_path: str) -> dict:
    """Load plant capacities from CSV and return as dictionary."""
    df = pd.read_csv(file_path)
    required_cols = {"fuel", "capacity"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"plant_capacity.csv must contain columns: {required_cols}")
    return dict(zip(df["fuel"], df["capacity"]))

def load_demand(
    file_path: str,
    start: Optional[Union[str, pd.Timestamp]] = None,
    end:   Optional[Union[str, pd.Timestamp]] = None,
    resample_method: str = "ME",
    zone: str = "DK_2",
    supply_factor: float = 0.5
) -> pd.DataFrame:
    """
    Load electricity demand from CSV, parse timestamps, select a zone column,
    limit to [start, end], and resample using SUM aggregation (default monthly).

    Parameters
    ----------
    file_path : str
        Path to CSV. The function expects the first column to be the datetime
        (e.g. 'utc_timestamp').
    start, end : str or pd.Timestamp, optional
        Inclusive date range to select. If None uses full available range.
    resample_method : str, default "M"
        Pandas offset alias for resampling (e.g. "M","MS","W","D","H").
        Month-end ("ME") is also supported as an alias for "M".
        "D" daily resampling sums all hours in the day.
    zone : str, default "DK_2"
        Electricity zone column to return. Matching is case-insensitive.

    Returns
    -------
    pd.DataFrame
        A single-column DataFrame indexed by datetime (period end for "M"),
        column named by the selected zone (original column name case preserved).
    """
    # Read CSV parsing the first column as dates
    df = pd.read_csv(file_path, parse_dates=[0])
    if df.shape[1] < 2:
        raise ValueError("CSV must contain a timestamp column plus at least one zone column.")

    # Use first column as datetime index
    date_col = df.columns[0]
    df = df.set_index(date_col)

    # Ensure datetime index and remove any timezone info (make tz-naive)
    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        # convert to UTC then drop tz info (robust for various tz types)
        df.index = df.index.tz_convert("UTC").tz_localize(None)

    df.index.name = date_col

    # Normalize column names map for case-insensitive matching (keep originals)
    col_map = {col.lower().strip(): col for col in df.columns}

    # Find requested zone (case-insensitive)
    zone_key = zone.lower().strip()
    if zone_key not in col_map:
        available = ", ".join(list(df.columns[:20]) + (["..."] if len(df.columns) > 20 else []))
        raise ValueError(f"Zone '{zone}' not found in CSV columns. Available (sample): {available}")

    selected_col = col_map[zone_key]

    # Coerce the selected column to numeric (non-numeric -> NaN)
    df[selected_col] = pd.to_numeric(df[selected_col], errors="coerce")

    # Determine start/end bounds
    if start is not None:
        start_ts = pd.to_datetime(start)
    else:
        start_ts = df.index.min()

    if end is not None:
        # Set end to the end of the month at 23:00 to include full month data
        end_ts = pd.to_datetime(end) + pd.offsets.MonthEnd(1) + pd.offsets.Hour(23)
    else:
        end_ts = df.index.max()

    if start_ts > end_ts:
        raise ValueError("`start` must be less than or equal to `end`.")

    # Select the requested time window (inclusive)
    df = df.loc[start_ts:end_ts]
    if df.empty:
        raise ValueError("No data in the selected date range.")

    # Resample and aggregate with SUM (NaNs ignored by sum)
    df = df[selected_col].resample(resample_method).sum()

    # Only supply a fraction of the demand
    df = df * supply_factor

    # Return as DataFrame with the original column name
    df = df.to_frame(name=selected_col)


    return df

# Example usage
if __name__ == "__main__":
    # Replace with actual file paths
    prices = load_prices("data/prices.csv")
    storage = load_storage("data/storage.csv")
    plant_capacity = load_plant_capacity("data/plant_capacity.csv")
    demand = load_demand("data/demand.csv")

    print("Prices:\n", prices.head())
    print("Storage:\n", storage)
    print("Plant Capacity:\n", plant_capacity)
    print("Demand:\n", demand.head())

