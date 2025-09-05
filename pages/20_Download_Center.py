from utils.safe import guard
import streamlit as st
from utils.io import paths
def main():
    st.title("📥 Download Center")
    p=paths()
    for label,key in [("Materials template","materials"),("Processes template","processes"),("BOM template","bom"),("Supplier quotes","quotes")]:
        f=p[key]
        try: st.download_button(f"Download {label}", data=f.read_bytes(), file_name=f.name, mime="text/csv")
        except FileNotFoundError: st.warning(f"Bestand ontbreekt: {f}")
guard(main)
