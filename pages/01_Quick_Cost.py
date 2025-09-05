import streamlit as st

from utils.io import load_bom, load_materials, load_processes, load_quotes
from utils.pricing import compute_costs
from utils.quotes import apply_best_quotes
from utils.safe import guard


def main():
    st.title("💸 Quick Cost (beste quotes)")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()
    quotes = load_quotes()
    df = compute_costs(apply_best_quotes(mats, quotes), procs, bom)
    st.dataframe(
        df[
            [
                "line_id",
                "material_id",
                "qty",
                "material_cost",
                "process_cost",
                "overhead",
                "margin",
                "total_cost",
            ]
        ]
    )
    st.metric("Totaal", f"EUR {df['total_cost'].sum():,.2f}")


guard(main)
