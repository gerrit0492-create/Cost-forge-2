from utils.safe import guard
import streamlit as st
from utils.market import load_market_csv, yoy_change
def main():
    st.title("📈 Marktdata (simple)")
    path = st.text_input("CSV-pad", "data/market.csv")
    df = load_market_csv(path)
    st.dataframe(df)
    series = st.text_input("Serie-naam")
    if series:
        yo = yoy_change(df, series)
        st.write("YoY:", "n.v.t." if yo is None else f"{yo*100:.2f}%")
guard(main)
