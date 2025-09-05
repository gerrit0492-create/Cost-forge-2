# tools/update_materials_from_market.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime
import os
import pandas as pd

DATA = Path("data")
HISTORY = DATA / "history"
MATS_CSV = DATA / "materials_db.csv"
QUOTES_CSV = DATA / "supplier_quotes.csv"
FACTORS_CSV = DATA / "market_factors.csv"  # optioneel lokaal
FACTORS_URL = os.getenv("MARKET_FACTORS_URL", "").strip()  # optioneel via GitHub secret

REQ_MATS = ["material_id", "description", "price_eur_per_kg"]
REQ_QUOTES = ["supplier", "material_id", "price_eur_per_kg", "lead_time_days", "valid_until", "preferred"]

def _read_csv_safe(p: Path, required: Optional[list[str]] = None) -> Optional[pd.DataFrame]:
    if not p.exists():
        return None
    df = pd.read_csv(p)
    if required:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{p}: ontbrekende kolommen: {missing}")
    return df

def _read_market_factors() -> Optional[pd.DataFrame]:
    if FACTORS_URL:
        try:
            return pd.read_csv(FACTORS_URL, comment="#")
        except Exception as e:
            print(f"⚠️ MARKET_FACTORS_URL niet leesbaar: {e}")
    if FACTORS_CSV.exists():
        try:
            return pd.read_csv(FACTORS_CSV, comment="#")
        except Exception as e:
            print(f"⚠️ {FACTORS_CSV} niet leesbaar: {e}")
    return None

def best_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    q = quotes.copy()
    if "preferred" not in q.columns: q["preferred"] = 0
    if "lead_time_days" not in q.columns: q["lead_time_days"] = 999_999
    q = q.sort_values(
        by=["material_id", "preferred", "price_eur_per_kg", "lead_time_days"],
        ascending=[True, False, True, True],
        kind="mergesort",
    )
    return q.groupby("material_id", as_index=False).first()

def apply_best_quotes_to_materials(mats: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    bq = best_quotes(quotes)[["material_id", "price_eur_per_kg"]].rename(columns={"price_eur_per_kg": "price_from_quote"})
    out = mats.merge(bq, on="material_id", how="left")
    if "price_eur_per_kg" not in out.columns:
        out["price_eur_per_kg"] = out["price_from_quote"]
    else:
        out["price_eur_per_kg"] = pd.to_numeric(out["price_eur_per_kg"], errors="coerce").fillna(out["price_from_quote"])
    return out.drop(columns=["price_from_quote"])

def apply_market_factors(mats: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    out = mats.copy()
    f = factors.copy()
    f.columns = [c.strip().lower() for c in f.columns]
    has_cmd = "commodity" in out.columns and "commodity" in f.columns

    by_mat: dict[tuple[str, str], pd.Series] = {}
    if "material_id" in f.columns:
        for _, r in f.iterrows():
            key = r.get("material_id")
            if pd.notna(key):
                by_mat[("material_id", str(key))] = r

    by_cmd: dict[tuple[str, str], pd.Series] = {}
    if has_cmd:
        for _, r in f.iterrows():
            key = r.get("commodity")
            if pd.notna(key):
                by_cmd[("commodity", str(key))] = r

    def _apply_row(price: float, r: pd.Series) -> float:
        pct = r.get("pct_change")
        fac = r.get("factor")
        v = price
        if pd.notna(pct):
            try: v *= (1 + float(pct) / 100.0)
            except Exception: pass
        if pd.notna(fac):
            try: v *= float(fac)
            except Exception: pass
        return v

    for i in range(len(out)):
        base = out.at[i, "price_eur_per_kg"]
        if pd.isna(base): continue
        applied = False
        k = ("material_id", str(out.at[i, "material_id"]))
        if k in by_mat:
            out.at[i, "price_eur_per_kg"] = _apply_row(base, by_mat[k])
            applied = True
        if has_cmd and not applied:
            k2 = ("commodity", str(out.at[i, "commodity"]))
            if k2 in by_cmd:
                out.at[i, "price_eur_per_kg"] = _apply_row(base, by_cmd[k2])
    return out

def save_history_snapshot(df: pd.DataFrame) -> Path:
    HISTORY.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d")
    snap = HISTORY / f"materials_{stamp}.csv"
    if not snap.exists():
        df.to_csv(snap, index=False)
        print(f"🗂️ Snapshot: {snap}")
    else:
        print(f"ℹ️ Snapshot bestaat al: {snap}")
    return snap

def main():
    mats = _read_csv_safe(MATS_CSV, REQ_MATS)
    if mats is None or mats.empty:
        raise SystemExit("materials_db.csv ontbreekt of is leeg")

    quotes = _read_csv_safe(QUOTES_CSV, REQ_QUOTES)
    if quotes is not None and not quotes.empty:
        mats = apply_best_quotes_to_materials(mats, quotes)

    factors = _read_market_factors()
    if factors is not None and not factors.empty:
        mats = apply_market_factors(mats, factors)

    if "price_eur_per_kg" in mats.columns:
        mats["price_eur_per_kg"] = pd.to_numeric(mats["price_eur_per_kg"], errors="coerce").round(4)

    before = pd.read_csv(MATS_CSV) if MATS_CSV.exists() else pd.DataFrame()
    changed = True
    try:
        changed = not mats.equals(before)
    except Exception:
        changed = True

    if not before.empty:
        save_history_snapshot(before)
    if changed:
        mats.to_csv(MATS_CSV, index=False)
        print("✅ materials_db.csv bijgewerkt.")
    else:
        print("ℹ️ Geen prijswijzigingen.")
    save_history_snapshot(mats)

if __name__ == "__main__":
    main()
