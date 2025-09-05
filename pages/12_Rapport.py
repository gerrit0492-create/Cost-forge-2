from utils.safe import guard
from utils.io import load_bom, load_materials, load_processes, load_quotes
from utils.pricing import compute_costs
from utils.quotes import apply_best_quotes

import pandas as pd
import streamlit as st


def main():
    st.title("📑 Rapport (Markdown)")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()
    quotes = load_quotes()

    df = compute_costs(apply_best_quotes(mats, quotes), procs, bom)

    # to_markdown gebruikt 'tabulate' als die geïnstalleerd is
    md = [
        "# Offerte-rapport",
        f"**Totaal (EUR):** {df['total_cost'].sum():,.2f}",
        "",
        df[["line_id","material_id","qty","material_cost","process_cost","overhead","margin","total_cost"]]
        .round(4)
        .to_markdown(index=False),
    ]
    content = "\n".join(md)
    st.download_button("Download rapport.md", content.encode("utf-8"), "rapport.md", "text/markdown")
    st.code(content, language="markdown")


guard(main)
