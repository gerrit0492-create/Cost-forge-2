# pages/99_Update_from_Public_CSV.py
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from utils.safe import guard


def edit_url_to_csv(edit_url: str, gid: str | int = 0) -> str:
    # werkt voor edit/view URL's → export CSV
    parts = urlparse(edit_url)
    seg = parts.path.strip("/").split("/")
    # verwacht: ["spreadsheets","d","<ID>","edit"] of met extra segmenten
    if len(seg) < 3 or seg[0] != "spreadsheets" or seg[1] != "d":
        raise ValueError("Onverwachte Google Sheets URL. Plak de edit/view link.")
    sheet_id = seg[2]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def read_public_csv(csv_url: str) -> pd.DataFrame:
    df = pd.read_csv(csv_url)
    # vaak handige casts
    for c in [
        "price_eur_per_kg",
        "machine_rate_eur_h",
        "labor_rate_eur_h",
        "overhead_pct",
        "margin_pct",
        "qty",
        "mass_kg",
        "runtime_h",
        "lead_time_days",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def write_and_snapshot(df: pd.DataFrame, target: Path, history_prefix: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target, index=False)
    hist_dir = Path("data/history")
    hist_dir.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.utcnow().strftime("%Y%m%d")
    snap = hist_dir / f"{history_prefix}{stamp}.csv"
    if not snap.exists():
        df.to_csv(snap, index=False)
    return target, snap


def main():
    st.title("🔗 Google Sheet (edit URL) → CSV import + snapshot")

    edit_url = st.text_input("Plak je Google Sheets *edit* URL hier", value="")
    gid = st.text_input("gid (tabblad-ID)", value="0", help="Meestal 0 = eerste tab.")

    t = st.radio(
        "Waar wil je dit voor gebruiken?",
        ["Materials", "Processes", "Quotes", "BOM"],
        horizontal=True,
    )
    mapping = {
        "Materials": ("data/materials_db.csv", "materials_"),
        "Processes": ("data/processes_db.csv", "processes_"),
        "Quotes": ("data/supplier_quotes.csv", "quotes_"),
        "BOM": ("data/bom_template.csv", "bom_"),
    }
    target_path, prefix = mapping[t]

    col1, col2 = st.columns(2)
    run = col1.button("Lees alleen")
    run_save = col2.button("Lees + Opslaan + Snapshot")

    if run or run_save:
        try:
            csv_url = edit_url_to_csv(edit_url, gid)
            st.code(csv_url, language="text")
            df = read_public_csv(csv_url)
        except Exception as e:
            st.error(f"Fout: {e}")
            return

        st.success(f"Ingelezen rijen: {len(df)}")
        st.dataframe(df, use_container_width=True)

        if run_save:
            path, snap = write_and_snapshot(df, Path(target_path), prefix)
            st.success(f"Opgeslagen → {path}")
            st.info(f"Snapshot → {snap.name}")
            st.download_button(
                "Download CSV", path.read_bytes(), file_name=Path(target_path).name, mime="text/csv"
            )
            if snap.exists():
                st.download_button(
                    "Download snapshot", snap.read_bytes(), file_name=snap.name, mime="text/csv"
                )


guard(main)
