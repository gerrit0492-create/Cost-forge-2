from utils.safe import guard
import streamlit as st, pandas as pd
from utils.io import load_materials, load_processes, load_bom
def neg(df, cols): return [c for c in cols if c in df.columns and (pd.to_numeric(df[c],errors="coerce")<0).any()]
def miss(df, cols): return [c for c in cols if c not in df.columns]
def main():
    st.title("🧪 Data Quality")
    mats=load_materials(); procs=load_processes(); bom=load_bom()
    m1=miss(mats,["material_id","price_eur_per_kg"]); m2=neg(mats,["price_eur_per_kg"])
    p1=miss(procs,["process_id","machine_rate_eur_h","labor_rate_eur_h","overhead_pct","margin_pct"])
    p2=neg(procs,["machine_rate_eur_h","labor_rate_eur_h","overhead_pct","margin_pct"])
    b1=miss(bom,["line_id","material_id","qty","mass_kg","process_route","runtime_h"])
    b2=neg(bom,["qty","mass_kg","runtime_h"])
    if any([m1,m2,p1,p2,b1,b2]):
        if m1: st.error(f"materials miss: {m1}")
        if m2: st.error(f"materials neg: {m2}")
        if p1: st.error(f"processes miss: {p1}")
        if p2: st.error(f"processes neg: {p2}")
        if b1: st.error(f"bom miss: {b1}")
        if b2: st.error(f"bom neg: {b2}")
    else:
        st.success("Alle basischecks OK")
guard(main)
