# utils/refresh_button.py
"""
Refresh button component with cache clearing
"""

import streamlit as st
from utils.api_client import clear_all_caches

def show_refresh_button(location: str = "sidebar", key: str = "refresh"):
    """
    Show refresh button that clears all caches
    
    Args:
        location: Where to show button ("sidebar" or "main")
        key: Unique key for the button
    
    Returns:
        True if button was clicked, False otherwise
    """
    container = st.sidebar if location == "sidebar" else st
    
    clicked = container.button(
        "🔄 Refresh Data",
        key=key,
        use_container_width=True,
        help="Clear cache and fetch fresh data from API"
    )
    
    if clicked:
        clear_all_caches()
        container.success("✓ Cache cleared! Refreshing...")
        st.rerun()
    
    return clicked

def show_last_update_time():
    """Show when data was last updated"""
    import datetime
    
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = datetime.datetime.now()
    
    elapsed = datetime.datetime.now() - st.session_state.last_refresh_time
    
    if elapsed.seconds < 60:
        time_str = "Just now"
    elif elapsed.seconds < 3600:
        mins = elapsed.seconds // 60
        time_str = f"{mins} min ago"
    else:
        hours = elapsed.seconds // 3600
        time_str = f"{hours}h ago"
    
    st.caption(f"Last updated: {time_str}")

def update_refresh_time():
    """Update the last refresh time"""
    import datetime
    st.session_state.last_refresh_time = datetime.datetime.now()