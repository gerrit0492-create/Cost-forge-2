from utils.safe import guard
import streamlit as st
from utils.io import load_materials, load_processes, load_bom, load_quotes
from utils.quotes import apply_best_quotes
from utils.pricing import compute_costs
from utils.pdf_export import make_offer_pdf
def main():
    st.title("🧾 Offerte PDF")
    mats=load_materials(); procs=load_processes(); bom=load_bom(); quotes=load_quotes()
    df=compute_costs(apply_best_quotes(mats,quotes),procs,bom)
    st.metric("Totaal", f"EUR {df['total_cost'].sum():,.2f}")
    st.dataframe(df[["line_id","material_id","qty","material_cost","process_cost","overhead","total_cost"]])
    st.download_button("Download offerte.pdf", make_offer_pdf(df), "offerte.pdf", "application/pdf")
guard(main)
