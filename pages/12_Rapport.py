from utils.safe import guard
import streamlit as st
from utils.io import load_materials, load_processes, load_bom, load_quotes
from utils.quotes import apply_best_quotes
from utils.pricing import compute_costs
def main():
    st.title("📑 Rapport (Markdown)")
    mats=load_materials(); procs=load_processes(); bom=load_bom(); quotes=load_quotes()
    df=compute_costs(apply_best_quotes(mats,quotes), procs, bom)
    md=["# Offerte-rapport",f"**Totaal (EUR):** {df['total_cost'].sum():,.2f}","",df.to_markdown(index=False)]
    content="\n".join(md)
    st.download_button("Download rapport.md", content.encode("utf-8"), "rapport.md", "text/markdown")
    st.code(content, language="markdown")
guard(main)
