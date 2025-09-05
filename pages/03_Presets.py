from utils.safe import guard
import streamlit as st
from utils.presets import load_presets, save_presets, PricingPreset
def main():
    st.title("⚙️ Presets (Overhead & Marge)")
    presets = load_presets()
    names = list(presets.keys())
    pick = st.selectbox("Preset", names, index=0 if names else None)
    if pick:
        p = presets[pick]
        over = st.number_input("Overhead %", value=p.overhead_pct*100, step=1.0)/100.0
        marg = st.number_input("Marge %", value=p.margin_pct*100, step=1.0)/100.0
        if st.button("Bewaar"):
            presets[pick]=PricingPreset(pick, over, marg); save_presets(presets); st.success("Opgeslagen")
    st.divider(); st.subheader("Nieuwe preset")
    nm = st.text_input("Naam")
    over_n=st.number_input("Overhead % (nieuw)",value=20.0)/100.0
    marg_n=st.number_input("Marge % (nieuw)",value=10.0)/100.0
    if st.button("Toevoegen") and nm:
        presets[nm]=PricingPreset(nm, over_n, marg_n); save_presets(presets); st.success("Preset toegevoegd")
guard(main)
