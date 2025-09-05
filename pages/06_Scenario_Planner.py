import streamlit as st

from utils.io import load_bom, load_materials, load_processes
from utils.pricing import compute_costs
from utils.safe import guard


def main():
    st.title("🧭 Scenario Planner")
    mats = load_materials().copy()
    procs = load_processes().copy()
    bom = load_bom().copy()

    mat_delta = st.sidebar.slider("Materiaalprijs ± %", -50, 50, 0, 5)
    labor_delta = st.sidebar.slider("Arbeidsloon ± %", -50, 50, 0, 5)
    margin_delta = st.sidebar.slider("Marge ± %-punten", -20, 20, 0, 1)

    mats["price_eur_per_kg"] *= 1 + mat_delta / 100.0
    procs["labor_rate_eur_h"] *= 1 + labor_delta / 100.0
    procs["margin_pct"] += margin_delta / 100.0

    df = compute_costs(mats, procs, bom)
    st.metric("Nieuw totaal (EUR)", f"{df['total_cost'].sum():,.2f}")
    st.dataframe(
        df[
            [
                "line_id",
                "material_id",
                "material_cost",
                "process_cost",
                "overhead",
                "margin",
                "total_cost",
            ]
        ]
    )


guard(main)
