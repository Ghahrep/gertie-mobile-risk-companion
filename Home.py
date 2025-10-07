# Home.py - FIXED FOR STREAMLIT CLOUD
"""
Mobile Risk Co-pilot - Home Page
Fixed: Replaced st.switch_page() with st.page_link()
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.api_client import get_api_client
from utils.portfolio_manager import get_portfolio, initialize_portfolio
from utils.insights_generator import generate_insights
from utils.loading_skeletons import (
    show_hero_card_skeleton,
    show_risk_score_skeleton,
    show_insight_card_skeleton,
    show_loading_message
)
from utils.portfolio_value import (
    get_portfolio_stats,
    initialize_portfolio_investment,
    format_currency,
    format_percent
)
from utils.refresh_button import show_refresh_button, show_last_update_time, update_refresh_time
from utils.tooltips import (
    show_metric_with_tooltip,
    show_learn_more_section,
    show_contextual_tip,
    tooltip_icon
)

# Initialize
initialize_portfolio()
initialize_portfolio_investment(default_amount=100000.0)  # $100K default

# Page config
st.set_page_config(
    page_title="Risk Co-pilot",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit elements
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-header {
        font-size: 1.75rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .hero-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        padding: 2rem;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: #f8f9fa;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 0.75rem 0;
    }
    
    .insight-card {
        background: white;
        border: 1px solid #e0e2e6;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .action-button {
        background: #1f77b4;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with refresh button
with st.sidebar:
    st.markdown("### 🏠 Navigation")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/2_Portfolio.py", label="Portfolio", icon="💼")
    st.page_link("pages/3_Risk.py", label="Risk Analysis", icon="⚠️")
    st.page_link("pages/4_Copilot.py", label="Co-pilot", icon="🤖")
    
    st.markdown("---")
    
    # Refresh button
    show_refresh_button(location="sidebar", key="home_refresh")
    show_last_update_time()
    
    st.markdown("---")
    st.caption("💡 Tip: Data is cached for faster loading")
    
    # Quick help guide in sidebar
    with st.expander("❓ Metric Guide", expanded=False):
        st.markdown("""
        **Quick Reference:**
        
        - **Risk Score:** Overall portfolio health (0-100)
        - **Portfolio Value:** Current worth of all holdings
        - **Volatility:** How much your value swings
        - **Sharpe Ratio:** Returns per unit of risk
        
        Tap any ℹ️ icon for detailed explanations.
        """)

# Main content
st.markdown("<h1 class='main-header'>📊 Portfolio Overview</h1>", unsafe_allow_html=True)

# Get portfolio
symbols, weights = get_portfolio()

if not symbols:
    st.info("👋 Welcome! Start by adding stocks to your portfolio.")
    
    # Educational content for new users
    with st.expander("📚 Learn: What is a portfolio?"):
        st.markdown("""
        A **portfolio** is a collection of investments (stocks, ETFs, bonds) that you own.
        
        **Why build a portfolio?**
        - **Diversification:** Spread risk across multiple assets
        - **Risk Management:** Balance growth with stability
        - **Goal Alignment:** Match investments to your financial goals
        
        **Get started:**
        1. Click "Portfolio" in the navigation
        2. Add 5-10 different holdings
        3. Adjust allocations based on your risk tolerance
        
        Need help? Use the Co-pilot to ask questions!
        """)
    
    st.stop()

# Create a container for dynamic content
content_container = st.container()

with content_container:
    # Show loading skeletons first
    hero_placeholder = st.empty()
    risk_score_placeholder = st.empty()
    insights_placeholder = st.empty()
    
    # Show skeletons
    with hero_placeholder.container():
        show_hero_card_skeleton()
    
    with risk_score_placeholder.container():
        show_risk_score_skeleton()
    
    with insights_placeholder.container():
        show_insight_card_skeleton(count=3)
    
    # Fetch data (cached for 5 minutes)
    try:
        # Convert to tuples for caching
        symbols_tuple = tuple(symbols)
        weights_tuple = tuple(weights)
        
        # Set shorter timeout for startup
        import socket
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)  # 10 second timeout
        
        try:
            client = get_api_client()
            
            # Get portfolio stats (includes real value calculation)
            portfolio_stats = get_portfolio_stats(symbols, weights)
            
            # Get health score (cached)
            health_data = client.get_portfolio_health(symbols_tuple, weights_tuple)
            
            # Get risk analysis (cached)
            risk_data = client.get_risk_analysis(symbols_tuple, weights_tuple, period="1year")
            
            # Generate insights (cached) - pass tuples for caching
            insights = generate_insights(symbols_tuple, weights_tuple, risk_data)
            
            # Update refresh time
            update_refresh_time()
            
        finally:
            # Restore original timeout
            socket.setdefaulttimeout(old_timeout)
        
        # Replace skeletons with real data
        
        # 1. Hero Card - Real Portfolio Value
        with hero_placeholder.container():
            st.markdown(f"""
            <div class="hero-card">
                <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">
                    Portfolio Value
                </div>
                <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {portfolio_stats['total_value_formatted']}
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">
                    {portfolio_stats['gain_loss_pct_formatted']} • {portfolio_stats['gain_loss_formatted']}
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 0.875rem; opacity: 0.9;">
                        {portfolio_stats['holdings_count']} Holdings
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add tooltip explanation
            with st.expander("ℹ️ What is Portfolio Value?", expanded=False):
                st.markdown(tooltip_icon("portfolio_value", inline=False))
        
        # 2. Risk Score
        with risk_score_placeholder.container():
            score = health_data.get('score', 50)
            status = health_data.get('status', 'Unknown')
            
            # Color based on score
            if score >= 80:
                color = "#28a745"
                emoji = "✅"
                scenario = "good_portfolio"
            elif score >= 60:
                color = "#ffc107"
                emoji = "⚠️"
                scenario = "low_sharpe"
            else:
                color = "#dc3545"
                emoji = "🔴"
                scenario = "high_risk"
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{emoji}</div>
                        <div style="font-size: 2.5rem; font-weight: bold; color: {color}; margin-bottom: 0.5rem;">
                            {score}
                        </div>
                        <div style="font-size: 1rem; color: #666; text-transform: capitalize;">
                            Risk Score: {status}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                # Learn More button
                if st.button("ℹ️ Learn", key="risk_score_learn", use_container_width=True):
                    st.session_state['show_risk_score_help'] = True
            
            # Show contextual help
            if st.session_state.get('show_risk_score_help', False):
                show_learn_more_section("risk_score", expanded=True)
                show_contextual_tip(scenario)
                if st.button("Close", key="close_risk_help"):
                    st.session_state['show_risk_score_help'] = False
                    st.rerun()
        
        # 3. Key Insights
        with insights_placeholder.container():
            st.markdown("### 💡 Key Insights")
            
            if insights and len(insights) > 0:
                for insight in insights[:3]:  # Top 3 insights
                    st.markdown(f"""
                    <div class="insight-card">
                        <div style="font-weight: 600; color: #1f77b4; margin-bottom: 0.5rem;">
                            {insight.get('emoji', '💡')} {insight.get('title', 'Insight')}
                        </div>
                        <div style="color: #666; font-size: 0.9rem;">
                            {insight.get('description', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No insights available yet. Check back after market analysis.")
        
        # Quick Actions - FIXED: Using st.page_link instead of st.switch_page
        st.markdown("### 🎯 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.page_link("pages/2_Portfolio.py", label="💼 Edit Portfolio", use_container_width=True)
        
        with col2:
            st.page_link("pages/3_Risk.py", label="📊 View Risk", use_container_width=True)
        
        with col3:
            st.page_link("pages/4_Copilot.py", label="🤖 Ask Co-pilot", use_container_width=True)
        
        # Holdings Summary
        with st.expander("📋 Holdings Details", expanded=False):
            for holding in portfolio_stats['holdings']:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{holding['symbol']}**")
                
                with col2:
                    st.write(f"{holding['weight']*100:.1f}%")
                
                with col3:
                    st.write(format_currency(holding['current_value']))
            
            st.markdown("---")
            # FIXED: Using st.page_link
            st.page_link("pages/2_Portfolio.py", label="✏️ Edit Portfolio", use_container_width=True)
        
    except Exception as e:
        # Clear skeletons and show error
        hero_placeholder.empty()
        risk_score_placeholder.empty()
        insights_placeholder.empty()
        
        st.error(f"⚠️ Error loading data: {str(e)}")
        st.info("Try refreshing using the button in the sidebar.")
        
        # Show basic info even on error
        if symbols:
            st.write(f"**Portfolio:** {', '.join(symbols)}")

# Footer
st.markdown("---")
st.caption("💡 **Tip**: Use the refresh button in the sidebar to update with the latest market data.")
st.caption("📊 Data is cached for 5 minutes for faster performance.")
st.caption("❓ Tap any ℹ️ icon to learn about metrics.")