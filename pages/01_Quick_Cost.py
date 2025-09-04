from __future__ import annotations
import streamlit as st
from utils.safe import guard
from utils.io import load_materials, load_processes, load_bom, load_quotes
from utils.quotes import apply_best_quotes
from utils.pricing import compute_costs

def main():
    st.title("💸 Quick Cost (beste quotes toegepast)")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()
    quotes = load_quotes()

    st.caption("Materialprijzen worden overschreven met beste supplier quotes (voorkeur → prijs → levertijd).")
    mats_q = apply_best_quotes(mats, quotes)

    df = compute_costs(mats_q, procs, bom)

    st.subheader("Calculated costs per line")
    st.dataframe(df[["line_id","material_id","qty","material_cost","process_cost","overhead","margin","total_cost"]])

    st.metric("📦 Offer total (EUR)", f"{df['total_cost'].sum():,.2f}")
    st.download_button("Export berekening (CSV)", df.to_csv(index=False).encode("utf-8"), "costs.csv", "text/csv")

guard(main)
