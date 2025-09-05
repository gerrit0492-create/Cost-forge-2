from utils.safe import guard
import streamlit as st, pandas as pd
from utils.io import load_bom
from utils.routing import compute_routing_cost, routing_summary
def main():
    st.title("🛠️ Routing Kosten")
    st.write("Upload routing.csv met kolommen: process_id,time_h_per_unit,setup_h")
    up = st.file_uploader("Upload routing.csv", type=["csv"])
    if up:
        routing = pd.read_csv(up)
        df = compute_routing_cost(load_bom(), routing)
        st.dataframe(df)
        st.subheader("Samenvatting")
        st.dataframe(routing_summary(df))
guard(main)
