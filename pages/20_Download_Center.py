from __future__ import annotations
import streamlit as st
from utils.safe import guard
from utils.io import paths

def main():
    st.title("📥 Download Center")
    p = paths()
    files = [
        ("Materials template","materials"),
        ("Processes template","processes"),
        ("BOM template","bom"),
        ("Supplier quotes","quotes"),
    ]
    for label, key in files:
        f = p[key]
        try:
            data = f.read_bytes()
            st.download_button(f"Download {label}", data=data, file_name=f.name, mime="text/csv")
        except FileNotFoundError:
            st.warning(f"Bestand ontbreekt: {f}")

guard(main)
