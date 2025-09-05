import pandas as pd
import streamlit as st

from utils.history import load_materials_history
from utils.safe import guard


def main():
    st.title("⏳ Materiaalprijs Historie")
    hist = load_materials_history()
    if hist.empty:
        st.info("Nog geen snapshots gevonden in data/history/. Wacht op de eerste weekly run.")
        return
    mats = sorted(hist["material_id"].dropna().unique().tolist())
    pick = st.selectbox("Materiaal", mats)
    sub = hist[hist["material_id"] == pick].sort_values("stamp")
    st.dataframe(sub, use_container_width=True)
    try:
        chart_df = sub[["stamp", "price_eur_per_kg"]].copy()
        chart_df["stamp"] = pd.to_datetime(chart_df["stamp"], format="%Y%m%d")
        chart_df = chart_df.set_index("stamp")
        st.line_chart(chart_df["price_eur_per_kg"])
    except Exception:
        pass


guard(main)
