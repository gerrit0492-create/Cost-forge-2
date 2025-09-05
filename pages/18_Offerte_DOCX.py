import streamlit as st

from utils.docx_export import make_offer_docx
from utils.io import load_bom, load_materials, load_processes, load_quotes
from utils.pricing import compute_costs
from utils.quotes import apply_best_quotes
from utils.safe import guard


def main():
    st.title("📄 Offerte DOCX")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()
    quotes = load_quotes()
    df = compute_costs(apply_best_quotes(mats, quotes), procs, bom)
    st.metric("Totaal", f"EUR {df['total_cost'].sum():,.2f}")
    st.dataframe(
        df[
            [
                "line_id",
                "material_id",
                "qty",
                "material_cost",
                "process_cost",
                "overhead",
                "total_cost",
            ]
        ]
    )
    st.download_button(
        "Download offerte.docx",
        make_offer_docx(df),
        "offerte.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


guard(main)
