import streamlit as st

from utils.io import load_bom, load_materials, load_processes
from utils.safe import guard
from utils.validators import check_missing, check_positive


def main():
    st.title("🧪 Data Quality")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()

    m1 = check_missing(mats, ["material_id", "price_eur_per_kg"])
    m2 = check_positive(mats, ["price_eur_per_kg"])

    p1 = check_missing(
        procs,
        ["process_id", "machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"],
    )
    p2 = check_positive(
        procs, ["machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"]
    )

    b1 = check_missing(
        bom, ["line_id", "material_id", "qty", "mass_kg", "process_route", "runtime_h"]
    )
    b2 = check_positive(bom, ["qty", "mass_kg", "runtime_h"])

    any_issue = any([m1, m2, p1, p2, b1, b2])
    if any_issue:
        if m1:
            st.error(f"materials miss: {m1}")
        if m2:
            st.error(f"materials neg: {m2}")
        if p1:
            st.error(f"processes miss: {p1}")
        if p2:
            st.error(f"processes neg: {p2}")
        if b1:
            st.error(f"bom miss: {b1}")
        if b2:
            st.error(f"bom neg: {b2}")
    else:
        st.success("Alle basischecks OK")


guard(main)
