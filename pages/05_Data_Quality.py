from __future__ import annotations
import streamlit as st
from utils.safe import guard
from utils.io import load_materials, load_processes, load_bom
from utils.validators import data_quality_report

def main():
    st.title("🧪 Data Quality")
    mats = load_materials()
    procs = load_processes()
    bom = load_bom()

    report = data_quality_report(mats, procs, bom)
    ok = True
    for section, issues in report.items():
        if issues:
            ok = False
            st.error(f"{section}:")
            for i in issues:
                st.write("• ", i)
        else:
            st.success(f"{section}: OK")

    if ok:
        st.balloons()
        st.info("Alle basiscontroles geslaagd.")

guard(main)
