import streamlit as st

st.set_page_config(
    page_title="Risk Companion",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 Mobile Risk Companion")
st.success("✅ App is running!")

# Test secrets
st.write("Testing secrets access...")

try:
    api_url = st.secrets.get("API_BASE_URL", "NOT_SET")
    fmp_key = st.secrets.get("FMP_API_KEY", "NOT_SET")
    
    st.write(f"API_BASE_URL: {api_url}")
    st.write(f"FMP_API_KEY: {'SET ✅' if fmp_key != 'NOT_SET' else 'NOT SET ❌'}")
except Exception as e:
    st.error(f"Error accessing secrets: {e}")

# Test imports
st.write("Testing imports...")

try:
    from utils import api_client
    st.success("✅ api_client imported")
except Exception as e:
    st.error(f"❌ api_client failed: {e}")

try:
    from utils import portfolio_manager
    st.success("✅ portfolio_manager imported")
except Exception as e:
    st.error(f"❌ portfolio_manager failed: {e}")

try:
    from utils import loading_skeletons
    st.success("✅ loading_skeletons imported")
except Exception as e:
    st.error(f"❌ loading_skeletons failed: {e}")

st.info("If you see this, the app started successfully!")