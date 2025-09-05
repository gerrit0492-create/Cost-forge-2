from pathlib import Path

import pandas as pd
import streamlit as st

from utils.safe import guard


def main():
    st.title("📥 BOM Import")
    up = st.file_uploader("Upload BOM CSV", type=["csv"])
    if up:
        df = pd.read_csv(up)
        Path("data/bom_template.csv").write_text(df.to_csv(index=False), encoding="utf-8")
        st.success("BOM opgeslagen naar data/bom_template.csv")
        st.dataframe(df.head())


guard(main)
