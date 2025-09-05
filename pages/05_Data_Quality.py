from utils.safe import guard
from utils.io import load_bom, load_materials, load_processes
from utils.validators import check_missing, check_positive, business_rules, summarize_rules, all_rules_ok
import streamlit as st


def main():
    st.title("🧪 Data Quality + Guardrails")

    mats = load_materials(); procs = load_processes(); bom = load_bom()

    # Structurele checks
    m1 = check_missing(mats, ["material_id", "price_eur_per_kg"])
    m2 = check_positive(mats, ["price_eur_per_kg"])
    p1 = check_missing(procs, ["process_id", "machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"])
    p2 = check_positive(procs, ["machine_rate_eur_h", "labor_rate_eur_h"])
    b1 = check_missing(bom, ["line_id", "material_id", "qty", "mass_kg", "process_route", "runtime_h"])
    b2 = check_positive(bom, ["qty", "mass_kg"])  # runtime mag 0 zijn

    any_issue = any([m1, m2, p1, p2, b1, b2])
    if any_issue:
        if m1: st.error(f"materials miss: {m1}")
        if m2: st.error(f"materials ≤0: {m2}")
        if p1: st.error(f"processes miss: {p1}")
        if p2: st.error(f"processes ≤0: {p2}")
        if b1: st.error(f"bom miss: {b1}")
        if b2: st.error(f"bom ≤0: {b2}")
    else:
        st.success("Structuur OK")

    # Guardrails
    st.subheader("Business rules")
    rules = business_rules(mats, procs, bom)
    st.code(summarize_rules(rules))
    if all_rules_ok(rules):
        st.success("Alle business rules OK")
    else:
        st.error("Business rules schendingen: zie boven.")


guard(main)
