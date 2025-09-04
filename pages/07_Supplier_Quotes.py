from __future__ import annotations
import streamlit as st
from utils.safe import guard
from utils.io import load_quotes, load_materials
from utils.quotes import best_quotes, join_with_materials

def main():
    st.title("🤝 Supplier Quotes")
    quotes = load_quotes()
    mats = load_materials()

    st.subheader("Alle ingelezen quotes")
    st.dataframe(quotes)

    st.subheader("Beste quotes per materiaal (voorkeur → prijs → levertijd)")
    best = best_quotes(quotes)
    st.dataframe(best)

    st.subheader("Materialen verrijkt met beste leverancier")
    enriched = join_with_materials(mats, best)
    st.dataframe(enriched)

    st.download_button("Export beste_quotes.csv", best.to_csv(index=False).encode("utf-8"),
                       file_name="beste_quotes.csv", mime="text/csv")

guard(main)
