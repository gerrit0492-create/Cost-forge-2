# tools/update_materials_from_market.py
from __future__ import annotations
from pathlib import Path
from typing import Optional

import pandas as pd


DATA = Path("data")
MATS_CSV = DATA / "materials_db.csv"
QUOTES_CSV = DATA / "supplier_quotes.csv"
FACTORS_CSV = DATA / "market_factors.csv"  # optioneel

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

def best_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    q = quotes.copy()
    # defaulten
    if "preferred" not in q.columns:
        q["preferred"] = 0
    if "lead_time_days" not in q.columns:
        q["lead_time_days"] = 999_999
    # sorteer: preferred desc, prijs asc, levertijd asc
    q = q.sort_values(
        by=["material_id", "preferred", "price_eur_per_kg", "lead_time_days"],
        ascending=[True, False, True, True],
        kind="mergesort",
    )
    # 1 per materiaal
    return q.groupby("material_id", as_index=False).first()

def apply_best_quotes_to_materials(mats: pd.DataFrame, quotes: pd.DataFrame) -> pd.DataFrame:
    """Vervang/aanvul prijs per kg met beste leveranciersquote (1-per-materiaal)."""
    bq = best_quotes(quotes)[["material_id", "price_eur_per_kg"]].rename(
        columns={"price_eur_per_kg": "price_from_quote"}
    )
    out = mats.merge(bq, on="material_id", how="left")
    # als prijs_eur_per_kg bestaat: vul ontbrekende prijzen aan met quote
    if "price_eur_per_kg" not in out.columns:
        out["price_eur_per_kg"] = out["price_from_quote"]
    else:
        out["price_eur_per_kg"] = out["price_eur_per_kg"].fillna(out["price_from_quote"])
    out.drop(columns=["price_from_quote"], inplace=True)
    return out

def apply_market_factors(mats: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    """Pas pct_change (%) of factor (multiplier) toe. Je kunt matchen op material_id of op 'commodity' als kolom bestaat in materials."""
    out = mats.copy()

    # Normaliseer kolomnamen
    cols = [c.lower() for c in factors.columns]
    factors.columns = cols

    # Ondersteun twee manieren:
    # 1) directe match op material_id
    # 2) match via commodity (als materials_db.csv een 'commodity' kolom heeft)
    has_commodity = "commodity" in out.columns and "commodity" in factors.columns

    # Bouw mapping per material_id
    per_material = {}
    if "material_id" in factors.columns:
        for _, r in factors.iterrows():
            key = r.get("material_id")
            if not pd.isna(key):
                per_material.setdefault(("material_id", str(key)), r)

    # Bouw mapping per commodity
    per_commodity = {}
    if has_commodity:
        for _, r in factors.iterrows():
            key = r.get("commodity")
            if not pd.isna(key):
                per_commodity.setdefault(("commodity", str(key)), r)

    # helper om één rij toe te passen
    def _apply_row(base_price: float, row: pd.Series) -> float:
        pct = row.get("pct_change")  # bv +5 = +5%
        fac = row.get("factor")      # bv 1.03 = +3%
        price = base_price
        if pd.notna(pct):
            try:
                price *= (1 + float(pct) / 100.0)
            except Exception:
                pass
        if pd.notna(fac):
            try:
                price *= float(fac)
            except Exception:
                pass
        return price

    # loop materialen
    for i in range(len(out)):
        base = out.at[i, "price_eur_per_kg"]
        if pd.isna(base):
            continue

        applied = False

        # 1) material_id factor
        key = ("material_id", str(out.at[i, "material_id"]))
        if key in per_material:
            out.at[i, "price_eur_per_kg"] = _apply_row(base, per_material[key])
            applied = True

        # 2) commodity factor (als aanwezig en geen material_id match)
        if has_commodity and not applied:
            key2 = ("commodity", str(out.at[i, "commodity"]))
            if key2 in per_commodity:
                out.at[i, "price_eur_per_kg"] = _apply_row(base, per_commodity[key2])
                applied = True

    return out

def main():
    mats = _read_csv_safe(MATS_CSV, REQ_MATS)
    if mats is None or mats.empty:
        raise SystemExit("materials_db.csv ontbreekt of is leeg")

    quotes = _read_csv_safe(QUOTES_CSV, REQ_QUOTES)
    if quotes is not None and not quotes.empty:
        mats = apply_best_quotes_to_materials(mats, quotes)

    factors = _read_csv_safe(FACTORS_CSV)  # optioneel, kolommen: material_id?, commodity?, pct_change?, factor?
    if factors is not None and not factors.empty:
        mats = apply_market_factors(mats, factors)

    # rond af
    if "price_eur_per_kg" in mats.columns:
        mats["price_eur_per_kg"] = pd.to_numeric(mats["price_eur_per_kg"], errors="coerce").round(4)

    # schrijf alleen bij wijziging
    before = pd.read_csv(MATS_CSV)
    changed = not mats.equals(before)

    if changed:
        mats.to_csv(MATS_CSV, index=False)
        print("✅ materials_db.csv bijgewerkt.")
    else:
        print("ℹ️ Geen prijswijzigingen gedetecteerd.")

if __name__ == "__main__":
    main()
