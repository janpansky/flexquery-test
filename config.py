import streamlit as st

# Configuration details
hostname = st.secrets["api"]["hostname"]
token = st.secrets["api"]["token"]
workspace_id = "ecommerce-parent"
data_source_id = "ecommerce-snowflake-v3"
