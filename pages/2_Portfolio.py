# pages/2_Portfolio.py
"""
Portfolio Editor - Manage Your Holdings
Add, remove, and adjust portfolio allocations with real-time feedback
"""

import streamlit as st
import plotly.graph_objects as go
from utils.portfolio_manager import (
    get_portfolio, 
    set_portfolio, 
    add_to_portfolio, 
    remove_from_portfolio,
    update_weight,
    initialize_portfolio
)
from utils.portfolio_value import (
    get_portfolio_stats,
    format_currency,
    format_percent,
    initialize_portfolio_investment
)
from utils.api_client import get_api_client
from utils.refresh_button import show_refresh_button, show_last_update_time
from utils.tooltips import show_metric_with_tooltip, tooltip_icon
from utils.loading_skeletons import show_chart_skeleton, show_metric_skeleton
from utils.performance_chart import show_performance_section
import time

st.set_page_config(
    page_title="Portfolio Editor",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize
initialize_portfolio()
initialize_portfolio_investment()

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .portfolio-header {
        font-size: 1.75rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #111827;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stat-label {
        font-size: 0.875rem;
        opacity: 0.9;
        margin-bottom: 0.25rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .holding-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .holding-symbol {
        font-weight: 600;
        color: #111827;
        font-size: 1.125rem;
    }
    
    .holding-details {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    .section-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    .add-holding-card {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .quick-action-btn {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .quick-action-btn:hover {
        border-color: #667eea;
        background: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏠 Navigation")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/2_Portfolio.py", label="Portfolio", icon="💼")
    st.page_link("pages/3_Risk.py", label="Risk Analysis", icon="⚠️")
    st.page_link("pages/4_Copilot.py", label="Co-pilot", icon="🤖")
    
    st.markdown("---")
    show_refresh_button(location="sidebar", key="portfolio_refresh")
    show_last_update_time()
    
    st.markdown("---")
    st.caption("💡 Changes save automatically")

# Main content
st.markdown("<h1 class='portfolio-header'>💼 Portfolio Editor</h1>", unsafe_allow_html=True)

# Get current portfolio
symbols, weights = get_portfolio()

if not symbols:
    st.info("👋 Start by adding holdings to your portfolio")
else:
    # Portfolio stats at the top
    stats_placeholder = st.empty()
    
    with stats_placeholder.container():
        try:
            stats = get_portfolio_stats(symbols, weights)
            
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-label">Total Portfolio Value</div>
                <div class="stat-value">{stats['total_value_formatted']}</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">
                    {stats['gain_loss_pct_formatted']} • {stats['gain_loss_formatted']} • {stats['holdings_count']} Holdings
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown("""
            <div class="stats-card">
                <div class="stat-label">Total Portfolio Value</div>
                <div class="stat-value">Loading...</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Portfolio visualization
    st.markdown('<div class="section-header">📊 Asset Allocation</div>', unsafe_allow_html=True)
    
    viz_placeholder = st.empty()
    
    with viz_placeholder.container():
        try:
            # Create donut chart
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=weights,
                hole=0.5,
                textposition='auto',
                textinfo='label+percent',
                marker=dict(
                    colors=['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'],
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>Allocation: %{percent}<br>Weight: %{value:.2%}<extra></extra>'
            )])
            
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                height=400,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            show_chart_skeleton(height=400)

    if symbols and weights:
        with st.expander("📈 Historical Performance", expanded=False):
            st.markdown("""
            <div style="background: #f0f9ff; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
                <strong>💡 Tip:</strong> Historical performance shows how your portfolio would have performed 
                over different time periods compared to the S&P 500 benchmark. Use the time period buttons 
                to see 1 month, 3 months, 6 months, 1 year, or year-to-date performance.
            </div>
            """, unsafe_allow_html=True)
            
            show_performance_section(symbols, weights)

        



# Current Holdings Section
st.markdown('<div class="section-header">📋 Current Holdings</div>', unsafe_allow_html=True)

if symbols:
    # Quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚖️ Rebalance to Equal Weight", use_container_width=True):
            equal_weights = [1.0 / len(symbols)] * len(symbols)
            set_portfolio(symbols, equal_weights)
            st.success("✓ Rebalanced to equal weights")
            time.sleep(0.5)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Holdings", use_container_width=True, type="secondary"):
            if 'confirm_clear' not in st.session_state:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm")
            else:
                set_portfolio([], [])
                del st.session_state.confirm_clear
                st.success("✓ Portfolio cleared")
                time.sleep(0.5)
                st.rerun()
    
    st.markdown("---")
    
    # Editable holdings
    for i, (symbol, weight) in enumerate(zip(symbols, weights)):
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="padding-top: 0.5rem;">
                <div class="holding-symbol">{symbol}</div>
                <div class="holding-details">{format_currency(stats['holdings'][i]['current_value'])}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Weight slider
            new_weight = st.slider(
                f"Allocation",
                min_value=0.0,
                max_value=1.0,
                value=float(weight),
                step=0.01,
                format="%.1f%%",
                key=f"weight_{symbol}_{i}",
                label_visibility="collapsed"
            )
            
            # Update weight if changed
            if abs(new_weight - weight) > 0.001:
                update_weight(symbol, new_weight)
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"remove_{symbol}_{i}", help=f"Remove {symbol}"):
                remove_from_portfolio(symbol)
                st.success(f"✓ Removed {symbol}")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")

# Add new holding section
st.markdown('<div class="section-header">➕ Add New Holding</div>', unsafe_allow_html=True)

with st.expander("Add Stock or ETF", expanded=len(symbols) == 0):
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        new_symbol = st.text_input(
            "Symbol",
            placeholder="e.g., AAPL, MSFT, SPY",
            key="new_symbol_input",
            label_visibility="collapsed"
        ).upper()
    
    with col2:
        new_allocation = st.number_input(
            "Allocation %",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            key="new_allocation",
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("Add", use_container_width=True, type="primary", key="add_new_holding"):
            if new_symbol:
                if new_symbol in symbols:
                    st.error(f"⚠️ {new_symbol} already in portfolio")
                else:
                    add_to_portfolio(new_symbol, new_allocation / 100)
                    st.success(f"✓ Added {new_symbol}")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.error("⚠️ Enter a symbol")

# Quick add popular holdings
st.markdown("### 🎯 Quick Add Popular Holdings")

popular_holdings = {
    "Tech": [
        {"symbol": "AAPL", "name": "Apple"},
        {"symbol": "MSFT", "name": "Microsoft"},
        {"symbol": "GOOGL", "name": "Google"},
        {"symbol": "NVDA", "name": "NVIDIA"}
    ],
    "Index ETFs": [
        {"symbol": "SPY", "name": "S&P 500"},
        {"symbol": "QQQ", "name": "Nasdaq 100"},
        {"symbol": "VTI", "name": "Total Market"},
        {"symbol": "IWM", "name": "Russell 2000"}
    ],
    "Bonds": [
        {"symbol": "TLT", "name": "20+ Year Treasury"},
        {"symbol": "BND", "name": "Total Bond"},
        {"symbol": "AGG", "name": "Aggregate Bonds"},
        {"symbol": "LQD", "name": "Investment Grade"}
    ],
    "Commodities": [
        {"symbol": "GLD", "name": "Gold"},
        {"symbol": "SLV", "name": "Silver"},
        {"symbol": "USO", "name": "Oil"},
        {"symbol": "DBA", "name": "Agriculture"}
    ]
}

category = st.selectbox("Category", list(popular_holdings.keys()), label_visibility="collapsed")

cols = st.columns(4)
for i, holding in enumerate(popular_holdings[category]):
    with cols[i]:
        if st.button(
            f"{holding['symbol']}\n{holding['name']}", 
            key=f"quick_add_{holding['symbol']}", 
            use_container_width=True
        ):
            if holding['symbol'] not in symbols:
                add_to_portfolio(holding['symbol'], 0.10)  # 10% allocation
                st.success(f"✓ Added {holding['symbol']}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.info(f"{holding['symbol']} already in portfolio")

# Portfolio presets
with st.expander("📦 Load Preset Portfolios"):
    st.markdown("**Choose a professionally balanced portfolio:**")
    
    presets = {
        "Aggressive Growth": {
            "symbols": ["QQQ", "ARKK", "NVDA", "TSLA"],
            "weights": [0.40, 0.30, 0.20, 0.10],
            "description": "High growth tech focus, high volatility"
        },
        "Balanced 60/40": {
            "symbols": ["SPY", "BND", "GLD"],
            "weights": [0.60, 0.30, 0.10],
            "description": "Classic balanced portfolio with gold hedge"
        },
        "Income Focus": {
            "symbols": ["VYM", "SCHD", "TLT", "LQD"],
            "weights": [0.30, 0.30, 0.20, 0.20],
            "description": "Dividend stocks and bonds for income"
        },
        "All-Weather": {
            "symbols": ["SPY", "TLT", "GLD", "DBC"],
            "weights": [0.30, 0.40, 0.15, 0.15],
            "description": "Ray Dalio inspired diversified portfolio"
        },
        "Conservative": {
            "symbols": ["BND", "AGG", "VYM", "USMV"],
            "weights": [0.40, 0.30, 0.20, 0.10],
            "description": "Low volatility, capital preservation focus"
        }
    }
    
    for preset_name, preset_data in presets.items():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            **{preset_name}**  
            <small style="color: #6b7280;">{preset_data['description']}</small>  
            <small style="color: #9ca3af;">{', '.join(preset_data['symbols'])}</small>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Load", key=f"preset_{preset_name}", use_container_width=True):
                set_portfolio(preset_data['symbols'], preset_data['weights'])
                st.success(f"✓ Loaded {preset_name}")
                time.sleep(0.5)
                st.rerun()

# Portfolio insights (if we have holdings)
if symbols and len(symbols) > 0:
    st.markdown("---")
    st.markdown('<div class="section-header">💡 Portfolio Insights</div>', unsafe_allow_html=True)
    
    try:
        client = get_api_client()
        symbols_tuple = tuple(symbols)
        weights_tuple = tuple(weights)
        risk_data = client.get_risk_analysis(symbols_tuple, weights_tuple)
        
        if 'metrics' in risk_data:
            metrics = risk_data['metrics']
            vol = metrics.get('annualized_volatility', 0) * 100
            sharpe = metrics.get('sharpe_ratio', 0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # NEW: Volatility with tooltip
                show_metric_with_tooltip(
                    label="Volatility",
                    value=f"{vol:.1f}%",
                    metric_key="volatility"
                )
            
            with col2:
                # NEW: Sharpe with tooltip
                show_metric_with_tooltip(
                    label="Sharpe Ratio",
                    value=f"{sharpe:.2f}",
                    metric_key="sharpe_ratio"
                )
            
            # NEW: Contextual recommendations with tooltips
            st.markdown("### 💡 Recommendations")
            
            if len(symbols) < 5:
                st.info("💡 **Limited Diversification:** Consider adding 5-10 holdings for better diversification")
                with st.expander("ℹ️ Why diversify?"):
                    st.markdown("""
                    **Diversification reduces risk without sacrificing returns.**
                    
                    - 5-10 holdings: Good diversification
                    - Single stock: 100% concentrated risk
                    - Mix sectors: Tech, healthcare, finance, etc.
                    
                    **Example:** If you only own AAPL and it drops 20%, you lose 20%. 
                    With 10 stocks, one 20% drop only costs you 2%.
                    """)
            
            if vol > 25:
                st.warning("⚠️ **High Volatility:** Your portfolio swings significantly. Consider adding defensive assets.")
                with st.expander("ℹ️ How to reduce volatility?"):
                    st.markdown("""
                    **Add defensive assets:**
                    - **Bonds:** TLT, BND, AGG (low volatility)
                    - **Defensive stocks:** USMV, VYM (stable dividends)
                    - **Gold:** GLD (crisis hedge)
                    
                    **Target:** 15-25% volatility for balanced portfolios
                    """)
            
            if sharpe < 0.5:
                st.warning("⚠️ **Low Risk-Adjusted Returns:** Consider portfolio optimization")
                with st.expander("ℹ️ What is Sharpe Ratio?"):
                    st.markdown(tooltip_icon("sharpe_ratio", inline=False))
    
    except Exception as e:
        st.info("💡 Add holdings to see portfolio insights")

# Bottom navigation
st.markdown("### 🎯 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💼 Edit Portfolio", use_container_width=True):
        st.switch_page("pages/2_Portfolio.py")

with col2:
    if st.button("📊 View Risk", use_container_width=True):
        st.switch_page("pages/3_Risk.py")

with col3:
    if st.button("🤖 Ask Co-pilot", use_container_width=True):
        st.switch_page("pages/4_Copilot.py")