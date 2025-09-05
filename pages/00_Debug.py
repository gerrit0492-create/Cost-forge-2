from utils.safe import guard
import streamlit as st, sys, platform
def main():
    st.title("🪲 Debug"); st.write("Python:", sys.version); st.write("Platform:", platform.platform())
guard(main)
