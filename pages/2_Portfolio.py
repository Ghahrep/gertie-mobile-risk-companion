# pages/2_Portfolio.py
"""
Portfolio Details Screen
Mobile-optimized view of holdings with risk DNA
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import get_api_client
import numpy as np

st.set_page_config(
    page_title="Portfolio",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .page-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    
    .holding-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .holding-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .ticker {
        font-size: 1.3rem;
        font-weight: bold;
        color: #111827;
    }
    
    .weight {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin-top: 0.75rem;
    }
    
    .metric {
        padding: 0.75rem;
        background: #f9fafb;
        border-radius: 8px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        margin-top: 0.25rem;
    }
    
    .insight-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        font-size: 0.875rem;
    }
    
    .insight-success {
        background: #d1fae5;
        border-left-color: #10b981;
    }
    
    .insight-warning {
        background: #fee2e2;
        border-left-color: #ef4444;
    }
    
    .summary-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .correlation-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .corr-low { background: #d1fae5; color: #065f46; }
    .corr-moderate { background: #fef3c7; color: #92400e; }
    .corr-high { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-header">
    <h2 style="margin: 0;">💼 Portfolio Analysis</h2>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
        Deep dive into your holdings
    </p>
</div>
""", unsafe_allow_html=True)

# Get portfolio from session state
if 'portfolio' in st.session_state:
    symbols = st.session_state.portfolio.get('symbols', [])
    weights = st.session_state.portfolio.get('weights', [])
else:
    symbols = []
    weights = []

if not symbols:
    st.warning("📊 No portfolio loaded")
    st.info("Load a portfolio from the home screen to see detailed analysis")
    
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    st.stop()

# Portfolio Visualization
st.markdown("### Allocation")

fig = go.Figure(data=[go.Pie(
    labels=symbols,
    values=weights if weights else [1/len(symbols)] * len(symbols),
    hole=0.5,
    marker=dict(colors=['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4'])
)])

fig.update_layout(
    showlegend=True,
    height=320,
    margin=dict(t=20, b=20, l=20, r=20),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Get risk analysis data
st.markdown("### Risk Analysis")

with st.spinner("Analyzing portfolio..."):
    try:
        client = get_api_client()
        risk_response = client.get_risk_analysis(symbols, weights)
        
        if 'metrics' in risk_response:
            metrics = risk_response['metrics']
            total_vol = metrics.get('annualized_volatility', 0)
            sharpe = metrics.get('sharpe_ratio', 0)
            max_dd = abs(metrics.get('max_drawdown_pct', 0))
            cvar = abs(metrics.get('portfolio_cvar_95', 0))
            
            # Overall metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="metric-label">Volatility</div>
                    <div class="metric-value">{total_vol:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">{sharpe:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="metric-label">Max Drawdown</div>
                    <div class="metric-value">{max_dd:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.error("Unable to load risk metrics")
            total_vol = 0.20
            sharpe = 1.0
            max_dd = 15.0
            cvar = 0.03
    
    except Exception as e:
        st.error(f"Error loading risk data: {str(e)}")
        total_vol = 0.20
        sharpe = 1.0
        max_dd = 15.0
        cvar = 0.03

st.markdown("---")

# Holdings Detail
st.markdown("### Holdings Detail")

# Try to get correlation data
try:
    corr_response = client.get_correlation_analysis(symbols)
    has_corr_data = corr_response.get('status') == 'success'
except:
    has_corr_data = False

# Display each holding
for i, symbol in enumerate(symbols):
    weight = weights[i] if weights else 1.0 / len(symbols)
    
    # Estimate risk contribution (simplified)
    # In reality, this would use marginal contribution to risk
    risk_contrib = weight if total_vol == 0 else (weight * total_vol) / total_vol
    
    # Estimate correlation (would come from correlation matrix)
    # For demo, using synthetic values
    if has_corr_data:
        try:
            # Get average correlation for this symbol
            avg_corr = 0.65  # Placeholder - extract from corr_response
        except:
            avg_corr = 0.65
    else:
        avg_corr = 0.65
    
    # Determine correlation status
    if avg_corr > 0.7:
        corr_status = "High"
        corr_class = "corr-high"
        corr_color = "#ef4444"
    elif avg_corr > 0.4:
        corr_status = "Moderate"
        corr_class = "corr-moderate"
        corr_color = "#f59e0b"
    else:
        corr_status = "Low"
        corr_class = "corr-low"
        corr_color = "#10b981"
    
    # Create expandable holding card
    with st.expander(f"**{symbol}** • {weight:.1%}", expanded=False):
        # Metrics grid
        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric">
                <div class="metric-label">Risk Contribution</div>
                <div class="metric-value">{risk_contrib:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric">
                <div class="metric-label">Correlation</div>
                <div class="metric-value">
                    <span class="correlation-badge {corr_class}">{corr_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Insights
        st.markdown("---")
        st.markdown("**💡 Co-pilot Insights**")
        
        # Generate contextual insights
        insights = []
        
        if risk_contrib > 0.30:
            insights.append({
                'type': 'warning',
                'message': f"⚠️ {symbol} contributes {risk_contrib:.0%} of total risk—consider rebalancing to reduce concentration."
            })
        
        if avg_corr > 0.75:
            insights.append({
                'type': 'warning',
                'message': f"⚠️ High correlation ({avg_corr:.2f}) with other holdings reduces diversification benefit."
            })
        
        if weight > 0.40:
            insights.append({
                'type': 'warning',
                'message': f"⚠️ Large position ({weight:.0%})—increases portfolio concentration risk."
            })
        
        if not insights:
            insights.append({
                'type': 'success',
                'message': f"✓ {symbol} is well-balanced in your portfolio with appropriate risk contribution."
            })
        
        # Display insights
        for insight in insights:
            insight_class = 'insight-success' if insight['type'] == 'success' else 'insight-warning'
            st.markdown(f"""
            <div class="insight-box {insight_class}">
                {insight['message']}
            </div>
            """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Deep Analysis", key=f"analyze_{symbol}", use_container_width=True):
                st.session_state['analysis_target'] = symbol
                st.switch_page("pages/4_Copilot.py")
        
        with col2:
            if st.button("🔄 Find Replacement", key=f"replace_{symbol}", use_container_width=True):
                st.session_state['replace_target'] = symbol
                st.switch_page("pages/4_Copilot.py")

st.markdown("---")

# Correlation Matrix (optional, expandable)
if has_corr_data:
    with st.expander("📈 Correlation Matrix"):
        st.info("View how your holdings move together")
        
        try:
            # Would display correlation heatmap here
            st.markdown("**Coming soon:** Interactive correlation heatmap")
            
            # For now, show a simplified version
            st.markdown("""
            **Understanding Correlations:**
            - **High (>0.7):** Assets move together - limited diversification
            - **Moderate (0.4-0.7):** Some diversification benefit
            - **Low (<0.4):** Good diversification - assets move independently
            """)
        except Exception as e:
            st.error(f"Error displaying correlations: {str(e)}")

# Portfolio Actions
st.markdown("---")
st.markdown("### Portfolio Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🎯 Optimize", use_container_width=True, type="primary"):
        st.session_state['action'] = 'optimization'
        st.switch_page("pages/4_Copilot.py")

with col2:
    if st.button("🛡️ Find Hedges", use_container_width=True, type="primary"):
        st.switch_page("pages/5_Hedging.py")

# Edit Portfolio option
with st.expander("✏️ Edit Portfolio"):
    st.markdown("**Current Holdings:**")
    
    # Display editable portfolio
    for i, (symbol, weight) in enumerate(zip(symbols, weights if weights else [1/len(symbols)] * len(symbols))):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.text_input("Symbol", value=symbol, key=f"edit_symbol_{i}", disabled=True)
        
        with col2:
            st.number_input("Weight", value=weight*100, key=f"edit_weight_{i}", min_value=0.0, max_value=100.0, step=1.0, format="%.1f")
        
        with col3:
            if st.button("🗑️", key=f"remove_{i}"):
                st.warning("Remove functionality coming soon")
    
    st.info("💡 Tip: Use the Co-pilot to get recommendations on portfolio changes")

# Bottom Navigation
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠", use_container_width=True, help="Home"):
        st.switch_page("Home.py")

with col2:
    st.button("💼", use_container_width=True, disabled=True, help="Portfolio")

with col3:
    if st.button("🔥", use_container_width=True, help="Risk"):
        st.switch_page("pages/3_Risk.py")

with col4:
    if st.button("❓", use_container_width=True, help="Co-pilot"):
        st.switch_page("pages/4_Copilot.py")