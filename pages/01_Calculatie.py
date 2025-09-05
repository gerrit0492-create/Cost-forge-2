from utils.safe import guard
import streamlit as st
from utils.io import load_materials, load_processes, load_bom, load_quotes
from utils.quotes import apply_best_quotes
from utils.pricing import compute_costs
def main():
    st.title("💸 Calculatie (compat)")
    mats=load_materials(); procs=load_processes(); bom=load_bom(); quotes=load_quotes()
    df=compute_costs(apply_best_quotes(mats,quotes), procs, bom)
    st.dataframe(df); st.metric("Totaal (EUR)", f"{df['total_cost'].sum():,.2f}")
guard(main)
