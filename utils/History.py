# utils/history.py
from pathlib import Path

import pandas as pd

HIST_DIR = Path("data/history")


def load_materials_history():
    if not HIST_DIR.exists():
        return pd.DataFrame(
            columns=["stamp", "material_id", "description", "commodity", "price_eur_per_kg"]
        )
    rows = []
    for p in sorted(HIST_DIR.glob("materials_*.csv")):
        stamp = p.stem.split("_")[-1]
        try:
            df = pd.read_csv(p)
            df["stamp"] = stamp
            rows.append(df)
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(
            columns=["stamp", "material_id", "description", "commodity", "price_eur_per_kg"]
        )
    out = pd.concat(rows, ignore_index=True)
    if "commodity" not in out.columns:
        out["commodity"] = None
    return out[["stamp", "material_id", "description", "commodity", "price_eur_per_kg"]]
