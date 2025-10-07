import streamlit as st

st.set_page_config(
    page_title="Risk Co-pilot",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📊 Mobile Risk Co-pilot")
st.success("✅ App is deployed and running!")

# Test secrets
import os
api_url = os.getenv("API_BASE_URL", "Not set")
st.write(f"API URL from secrets: {api_url}")

# Test navigation
st.markdown("### Navigation Test")
st.page_link("Home.py", label="🏠 Home")
