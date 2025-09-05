import streamlit as st
def guard(fn):
    try: fn()
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        st.stop()
