import streamlit as st

from utils.io import load_materials, load_quotes
from utils.quotes import best_quotes, join_with_materials
from utils.safe import guard


def main():
    st.title("🤝 Supplier Quotes")
    quotes = load_quotes()
    mats = load_materials()
    best = best_quotes(quotes)
    st.subheader("Beste quotes per materiaal")
    st.dataframe(best)
    st.subheader("Materialen verrijkt met beste leverancier")
    st.dataframe(join_with_materials(mats, best))


guard(main)
