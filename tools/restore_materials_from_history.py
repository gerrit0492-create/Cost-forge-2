# tools/restore_materials_from_history.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
import os
import sys
import pandas as pd

DATA = Path("data")
HISTORY = DATA / "history"
MATS = DATA / "materials_db.csv"

def pick_snapshot(arg: Optional[str]) -> Path:
    """
    Kies een snapshotbestand uit data/history:
    - arg == "latest" of leeg  -> nieuwste materials_YYYYMMDD.csv
    - arg == "YYYYMMDD"        -> exact die datum
    - arg eindigt op .csv      -> gebruik dat bestandspad onder data/history
    """
    if not HISTORY.exists():
        raise FileNotFoundError(f"Geen history map: {HISTORY}")
    snaps = sorted(HISTORY.glob("materials_*.csv"))
    if not snaps:
        raise FileNotFoundError("Geen snapshots gevonden in data/history/")
    if not arg or arg.lower() == "latest":
        return snaps[-1]
    arg = arg.strip()
    if arg.endswith(".csv"):
        p = HISTORY / arg
        if not p.exists():
            raise FileNotFoundError(f"Snapshot bestaat niet: {p}")
        return p
    # assume pure date
    p = HISTORY / f"materials_{arg}.csv"
    if not p.exists():
        raise FileNotFoundError(f"Snapshot bestaat niet: {p}")
    return p

def show_diff(before: pd.DataFrame, after: pd.DataFrame) -> str:
    """Eenvoudige diff-samenvatting."""
    def keycols(df: pd.DataFrame):
        # material_id is onze sleutel
        return set(df["material_id"].astype(str)) if "material_id" in df.columns else set()
    kb = keycols(before)
    ka = keycols(after)
    added = sorted(list(ka - kb))
    removed = sorted(list(kb - ka))
    changed = []
    common = sorted(list(kb & ka))
    b = before.set_index("material_id")
    a = after.set_index("material_id")
    for mid in common:
        vb = b.loc[mid].to_dict()
        va = a.loc[mid].to_dict()
        # toon alleen relevante kolommen
        fields = ["price_eur_per_kg", "commodity", "description"]
        rowchg = []
        for f in fields:
            if vb.get(f) != va.get(f):
                rowchg.append(f"{f}: {vb.get(f)} -> {va.get(f)}")
        if rowchg:
            changed.append(f"{mid}: " + "; ".join(rowchg))
    lines = []
    lines.append(f"Toegevoegd: {len(added)} | Verwijderd: {len(removed)} | Gewijzigd: {len(changed)}")
    if added:
        lines.append(" + " + ", ".join(added[:10]) + (" …" if len(added) > 10 else ""))
    if removed:
        lines.append(" - " + ", ".join(removed[:10]) + (" …" if len(removed) > 10 else ""))
    if changed:
        lines.append(" ~ " + " | ".join(changed[:5]) + (" …" if len(changed) > 5 else ""))
    return "\n".join(lines)

def main():
    snap_arg = os.getenv("SNAPSHOT", "latest")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    snap = pick_snapshot(snap_arg)
    print(f"🔎 Gekozen snapshot: {snap}")

    if not MATS.exists():
        raise FileNotFoundError(f"{MATS} ontbreekt; niets om te overschrijven.")

    before = pd.read_csv(MATS)
    after = pd.read_csv(snap)

    # minimale sanity: moet kolommen bevatten
    required = {"material_id", "price_eur_per_kg"}
    missing = required - set(after.columns)
    if missing:
        raise ValueError(f"Snapshot mist verplichte kolommen: {missing}")

    # diff tonen
    summary = show_diff(before, after)
    print("=== DIFF SAMENVATTING ===")
    print(summary)

    if dry_run:
        print("🧪 Dry-run: geen wijzigingen geschreven.")
        return

    # schrijf restore
    after.to_csv(MATS, index=False)
    print(f"✅ Hersteld materials_db.csv vanaf {snap.name}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        sys.exit(1)
