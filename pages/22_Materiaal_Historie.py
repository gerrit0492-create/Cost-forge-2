from utils.safe import guard
from utils.history import (
    load_materials,
    save_snapshot_current,
    build_history_df,
    get_price_series,
    diff_vs_latest,
    find_anomalies,
)

import pandas as pd
import streamlit as st


def main():
    st.title("📈 Materiaal-historie & snapshots")

    mats = load_materials()
    if mats.empty:
        st.error("materials_db.csv is leeg.")
        return

    # Keuze materiaal
    mid = st.selectbox("Kies materiaal", mats["material_id"].astype(str).unique())
    series = get_price_series(mid)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Snapshot van huidige materials opslaan"):
            p = save_snapshot_current()
            st.success(f"Snapshot opgeslagen: {p.name}")

    with c2:
        dif = diff_vs_latest()
        if not dif.empty:
            anomalies = find_anomalies(dif)
            st.metric("Afwijkingen > 25%", len(anomalies))
            if len(anomalies):
                with st.expander("Toon afwijkingen vs. laatste snapshot"):
                    st.dataframe(
                        anomalies[["material_id", "old_price", "new_price", "pct_change"]]
                        .sort_values("pct_change"),
                        use_container_width=True,
                    )

    st.subheader(f"Historie voor {mid}")
    if series.empty or series["price_eur_per_kg"].isna().all():
        st.info("Geen historie gevonden voor dit materiaal.")
    else:
        # Grafiek
        chart = series.rename(columns={"price_eur_per_kg": "EUR/kg"}).set_index("date")
        st.line_chart(chart)

        st.dataframe(series, use_container_width=True)


guard(main)
