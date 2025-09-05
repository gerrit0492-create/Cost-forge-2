import streamlit as st

from utils.io import load_materials, load_quotes
from utils.quotes import best_quotes, join_with_materials
from utils.safe import guard


def main():
    st.title("🔗 Materiaalbronnen")
    mats = load_materials()
    quotes = load_quotes()
    best = best_quotes(quotes)
    st.subheader("Beste quotes")
    st.dataframe(best)
    st.subheader("Materialen + leverancier")
    st.dataframe(join_with_materials(mats, best))


guard(main)
