# main_app.py
import streamlit as st

# Import your existing files
from config_form import show_config_form
from network_dashboard import show_dashboard

# Page setup
st.set_page_config(page_title="Network Management", layout="wide")

openai_key = st.secrets["api_keys"]["OPENAI_API_KEY"]

# Sidebar navigation
st.sidebar.title("Network Tools")
page = st.sidebar.selectbox("Choose a page:", ["Dashboard", "Configuration"])

# Page routing
if page == "Dashboard":
    show_dashboard()
elif page == "Configuration":
    show_config_form()