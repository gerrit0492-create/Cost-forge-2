from pathlib import Path

import pandas as pd


def load_market_csv(path):
    p = Path(path)
    if not p.exists():
        return pd.DataFrame(columns=["series", "date", "value"])
    return pd.read_csv(p)


def yoy_change(df, series):
    sub = df[df["series"] == series].sort_values("date")
    if len(sub) < 13:
        return None
    latest = pd.to_numeric(sub["value"].iloc[-1], errors="coerce")
    prev = pd.to_numeric(sub["value"].iloc[-13], errors="coerce")
    if prev == 0 or pd.isna(prev) or pd.isna(latest):
        return None
    return (latest - prev) / prev
