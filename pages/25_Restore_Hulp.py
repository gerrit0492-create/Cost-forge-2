from pathlib import Path

import streamlit as st

H = Path("data/history")
st.title("🆘 Restore Hulp (read-only)")
if not H.exists():
    st.info("Nog geen snapshots in data/history/. Draai eerst de Weekly Market Update.")
else:
    snaps = sorted([p.name for p in H.glob("materials_*.csv")])
    if not snaps:
        st.info("Geen snapshots gevonden.")
    else:
        st.write(f"Gevonden snapshots: {len(snaps)}")
        st.table({"snapshots": snaps})
        st.caption(
            "Start het herstel in GitHub → Actions → “Panic Button: Restore materials_db.csv from history”."
        )
