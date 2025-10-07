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
st.page_link("pages/2_Portfolio.py", label="💼 Portfolio")
st.page_link("pages/3_Risk.py", label="🔥 Risk")
st.page_link("pages/4_Copilot.py", label="🤖 Ask")