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
FACTORS_CSV = DATA / "market_factors.csv"  # optioneel (lokaal)
# Optioneel: externe bron (Google Sheet → CSV export URL) via env var
FACTORS_URL = os.getenv("MARKET_FACTORS_URL", "").strip()  # set in GitHub Secret

REQ_MATS = ["material_id", "description", "price_eur_per_kg"]
REQ_QUOTES = [
    "supplier",
    "material_id",
    "price_eur_per_kg",
    "lead_time_days",
    "valid_until",
    "preferred",
]


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
    """Laad market_factors uit (1) URL (secret) of (2) lokaal CSV."""
    # Probeer eerst URL (Google Sheet CSV export of andere CSV endpoint)
    if FACTORS_URL:
        try:
            df = pd.read_csv(FACTORS_URL, comment="#")
            return df
        except Exception as e:
            print(f"⚠️ Kon MARKET_FACTORS_URL niet lezen: {e}")

    # Valt terug op lokaal CSV
    if FACTORS_CSV.exists():
        try:
            df = pd.read_csv(FACTORS_CSV, comment="#")
            return df
        except Exception as e:
            print(f"⚠️ Kon {FACTORS_CSV} niet lezen: {e}")
    return None


def best_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    q = quotes.copy()
    # defaults
    if "preferred" not in q.columns:
        q["preferred"] = 0
    if "lead_time_days" not in q.columns:
        q["lead_time_days"] = 999_999
    # Sorteer: preferred desc, prijs asc, levertijd asc
    q = q.sort_values(
        by=["material_id", "preferred", "price_eur_per_kg", "lead_time_days"],
        ascending=[True, False, True, True],
        kind="mergesort",
    )
    return q.groupby("material_id", as_index=False).first()


def apply_best_quotes_to_materials(mats: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    """Vervang/aanvul prijs per kg met beste leveranciersquote (1-per-materiaal)."""
    bq = best_quotes(quotes)[["material_id", "price_eur_per_kg"]].rename(
        columns={"price_eur_per_kg": "price_from_quote"}
    )
    out = mats.merge(bq, on="material_id", how="left")
    # als prijs_eur_per_kg bestaat: vul NaN aan met quote
    if "price_eur_per_kg" not in out.columns:
        out["price_eur_per_kg"] = out["price_from_quote"]
    else:
        out["price_eur_per_kg"] = pd.to_numeric(out["price_eur_per_kg"], errors="coerce")
        out["price_eur_per_kg"] = out["price_eur_per_kg"].fillna(out["price_from_quote"])
    out.drop(columns=["price_from_quote"], inplace=True)
    return out


def apply_market_factors(mats: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    """
    Pas pct_change (%) of factor (multiplier) toe. Match op:
      1) material_id (direct)
      2) commodity (als 'commodity' kolom in materials_db.csv én in factors)
    Kolommen in factors (case-insensitive): material_id?, commodity?, pct_change?, factor?
    """
    out = mats.copy()
    # normaliseer kolomnamen (lowercase)
    factors = factors.copy()
    factors.columns = [c.strip().lower() for c in factors.columns]

    has_commodity = "commodity" in out.columns and "commodity" in factors.columns

    # Index per material_id
    by_mat: dict[tuple[str, str], pd.Series] = {}
    if "material_id" in factors.columns:
        for _, r in factors.iterrows():
            key = r.get("material_id")
            if pd.notna(key):
                by_mat[("material_id", str(key))] = r

    # Index per commodity
    by_cmd: dict[tuple[str, str], pd.Series] = {}
    if has_commodity:
        for _, r in factors.iterrows():
            key = r.get("commodity")
            if pd.notna(key):
                by_cmd[("commodity", str(key))] = r

    def _apply_row(price: float, row: pd.Series) -> float:
        pct = row.get("pct_change")
        fac = row.get("factor")
        new = price
        if pd.notna(pct):
            try:
                new *= (1 + float(pct) / 100.0)
            except Exception:
                pass
        if pd.notna(fac):
            try:
                new *= float(fac)
            except Exception:
                pass
        return new

    for i in range(len(out)):
        base = out.at[i, "price_eur_per_kg"]
        if pd.isna(base):
            continue
        applied = False

        # eerst material_id
        k = ("material_id", str(out.at[i, "material_id"]))
        if k in by_mat:
            out.at[i, "price_eur_per_kg"] = _apply_row(base, by_mat[k])
            applied = True

        # dan commodity (als nog niet toegepast)
        if has_commodity and not applied:
            k2 = ("commodity", str(out.at[i, "commodity"]))
            if k2 in by_cmd:
                out.at[i, "price_eur_per_kg"] = _apply_row(base, by_cmd[k2])

    return out


def save_history_snapshot(df: pd.DataFrame) -> Path:
    """Sla materials_db.csv snapshot op in data/history/materials_YYYYMMDD.csv"""
    HISTORY.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d")
    snap = HISTORY / f"materials_{stamp}.csv"
    # Schrijf alleen als nog niet bestaat voor die dag
    if not snap.exists():
        df.to_csv(snap, index=False)
        print(f"🗂️ Snapshot geschreven: {snap}")
    else:
        print(f"ℹ️ Snapshot bestond al: {snap}")
    return snap


def main():
    mats = _read_csv_safe(MATS_CSV, REQ_MATS)
    if mats is None or mats.empty:
        raise SystemExit("materials_db.csv ontbreekt of is leeg")

    # Quotes → vul beste prijzen aan (optioneel)
    quotes = _read_csv_safe(QUOTES_CSV, REQ_QUOTES)
    if quotes is not None and not quotes.empty:
        mats = apply_best_quotes_to_materials(mats, quotes)

    # Market factors → pas toe (URL of lokaal)
    factors = _read_market_factors()
    if factors is not None and not factors.empty:
        mats = apply_market_factors(mats, factors)

    # afronden
    if "price_eur_per_kg" in mats.columns:
        mats["price_eur_per_kg"] = pd.to_numeric(mats["price_eur_per_kg"], errors="coerce").round(4)

    # schrijf alleen bij echte wijziging
    before = pd.read_csv(MATS_CSV) if MATS_CSV.exists() else pd.DataFrame()
    changed = True
    try:
        changed = not mats.equals(before)
    except Exception:
        # Als kolomvolgorde/typen verschillen, forceren we write
        changed = True

    # Altijd eerst snapshot van "voor update" (alleen als changed of history leeg)
    if not before.empty:
        save_history_snapshot(before)

    if changed:
        mats.to_csv(MATS_CSV, index=False)
        print("✅ materials_db.csv bijgewerkt.")
    else:
        print("ℹ️ Geen prijswijzigingen gedetecteerd.")

    # Ook snapshot van "na update"
    save_history_snapshot(mats)


if __name__ == "__main__":
    main()
