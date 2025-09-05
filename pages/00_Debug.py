import platform
import sys

import streamlit as st

from utils.safe import guard


def main():
    st.title("🪲 Debug")
    st.write("Python:", sys.version)
    st.write("Platform:", platform.platform())


guard(main)
