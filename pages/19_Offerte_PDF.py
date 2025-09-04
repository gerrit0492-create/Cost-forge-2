from __future__ import annotations
import streamlit as st
from utils.safe import guard
from utils.io import load_materials, load_processes, load_bom, load_quotes
from utils.quotes import apply_best_quotes
from utils.pricing import compute_costs
from utils.pdf_export import make_offer_pdf

def main():
    st.title("🧾 Offerte PDF export (met beste quotes)")
    mats = load_materials()
    quotes = load_quotes()
    procs = load_processes()
    bom = load_bom()

    mats_q = apply_best_quotes(mats, quotes)
    df = compute_costs(mats_q, procs, bom)

    st.metric("Totaal", f"EUR {df['total_cost'].sum():,.2f}")
    st.dataframe(df[["line_id","material_id","qty","material_cost","process_cost","overhead","total_cost"]])

    pdf_bytes = make_offer_pdf(df, title="Offerte — Cost Forge")
    st.download_button("Download offerte.pdf", data=pdf_bytes, file_name="offerte.pdf",
                       mime="application/pdf")

guard(main)
