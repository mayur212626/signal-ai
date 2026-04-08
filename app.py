import streamlit as st
st.set_page_config(page_title="SIGNAL", page_icon="📡", layout="wide")
st.title("📡 SIGNAL")
st.write("Sales Intelligence & Gap Analysis Layer")
# TODO: sidebar, pipeline trigger, results tabs

# sidebar: transcript selector + run button
with st.sidebar:
    st.markdown("## Select Calls")
    # multiselect placeholder
    run_btn = st.button("Run Analysis")
