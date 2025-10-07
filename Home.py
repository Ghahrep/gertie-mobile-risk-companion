# Home.py
"""
Mobile App Home Screen - iOS-inspired design
Portfolio overview with immediate risk visibility
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import get_api_client

st.set_page_config(
    page_title="Portfolio Risk App",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced iOS-inspired CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Portfolio Card - iOS style gradient */
    .portfolio-hero {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
    }
    
    .portfolio-label {
        font-size: 0.875rem;
        opacity: 0.9;
        margin-bottom: 0.25rem;
    }
    
    .portfolio-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .portfolio-change {
        font-size: 1.125rem;
        opacity: 0.95;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Risk Score Card - iOS style */
    .risk-hero {
        background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
    }
    
    .risk-score-large {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .risk-context {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.875rem;
        backdrop-filter: blur(10px);
    }
    
    /* Stress Scenario Cards - horizontal scroll */
    .scenarios-container {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding: 0.5rem 0 1rem 0;
        margin: 0 -1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .scenario-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        min-width: 140px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 3px solid var(--border-color);
        flex-shrink: 0;
    }
    
    .scenario-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .scenario-loss {
        font-size: 1.75rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
        color: var(--text-color);
    }
    
    .scenario-name {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Holdings List - iOS style */
    .holdings-container {
        background: white;
        border-radius: 24px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .holding-row {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .holding-row:last-child {
        border-bottom: none;
    }
    
    .holding-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1rem;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }
    
    .holding-info {
        flex: 1;
    }
    
    .holding-symbol {
        font-weight: 600;
        font-size: 0.875rem;
        color: #111827;
    }
    
    .holding-weight {
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    .holding-price {
        text-align: right;
        margin-right: 0.5rem;
    }
    
    .holding-price-value {
        font-weight: 600;
        font-size: 0.875rem;
        color: #111827;
    }
    
    .holding-change {
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .change-positive { color: #10b981; }
    .change-negative { color: #ef4444; }
    
    /* Quick Action Grid */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin: 1rem 0;
    }
    
    .action-button {
        background: white;
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .action-button:active {
        transform: scale(0.95);
    }
    
    .action-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .action-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: #111827;
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    .section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
    }
    
    .section-action {
        font-size: 0.875rem;
        color: #3b82f6;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'NVDA'],
        'weights': [0.25, 0.25, 0.25, 0.25]
    }

# Get current portfolio
symbols = st.session_state.portfolio.get('symbols', [])
weights = st.session_state.portfolio.get('weights', [])

if symbols and len(symbols) > 0:
    # Portfolio Value Hero Card (iOS style)
    st.markdown("""
    <div class="portfolio-hero">
        <div class="portfolio-label">Total Portfolio</div>
        <div class="portfolio-value">$127,485</div>
        <div class="portfolio-change">
            <span>↗</span>
            <span>+$3,247 (2.61%)</span>
            <span style="opacity: 0.7; margin-left: auto; font-size: 0.75rem;">Today</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get risk data
    try:
        client = get_api_client()
        risk_response = client.get_risk_analysis(symbols, weights)
        
        if 'metrics' in risk_response:
            vol = risk_response['metrics'].get('annualized_volatility', 0)
            sharpe = risk_response['metrics'].get('sharpe_ratio', 0)
            
            # Calculate risk score (0-100)
            # Lower volatility = higher score, adjusted for realistic ranges
            risk_score = max(0, min(100, int((1 - min(vol, 0.5) / 0.5) * 100)))
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = "Low Risk"
                risk_color = "#10b981"
            elif risk_score >= 40:
                risk_level = "Moderate Risk"
                risk_color = "#f97316"
            else:
                risk_level = "High Risk"
                risk_color = "#ef4444"
        else:
            risk_score = 68
            risk_level = "Moderate Risk"
            risk_color = "#f97316"
            vol = 0.20
            sharpe = 1.2
    except Exception as e:
        risk_score = 68
        risk_level = "Moderate Risk"
        risk_color = "#f97316"
        vol = 0.20
        sharpe = 1.2
    
    # Risk Score Card (iOS style with circular gauge)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: white; border-radius: 24px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.25rem;">Risk Score</div>
            <div style="font-size: 2.5rem; font-weight: bold; color: {risk_color}; margin: 0.5rem 0;">
                {risk_score}<span style="font-size: 1.25rem; opacity: 0.6;">/100</span>
            </div>
            <div style="font-size: 0.75rem; color: #6b7280; margin-bottom: 1rem;">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Create circular progress ring (CSS-based, more reliable than Plotly gauge)
        progress = risk_score
        circumference = 2 * 3.14159 * 32
        stroke_dashoffset = circumference - (progress / 100 * circumference)
        
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 120px;">
            <svg width="80" height="80" style="transform: rotate(-90deg);">
                <circle cx="40" cy="40" r="32" stroke="#f3f4f6" stroke-width="8" fill="none" />
                <circle 
                    cx="40" 
                    cy="40" 
                    r="32" 
                    stroke="{risk_color}" 
                    stroke-width="8" 
                    fill="none"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{stroke_dashoffset}"
                    stroke-linecap="round"
                    style="transition: stroke-dashoffset 0.3s ease;"
                />
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions Grid (iOS style)
    st.markdown('<div class="section-header"><div class="section-title">Quick Actions</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔥\n\n**Analyze**", use_container_width=True, key="analyze_btn"):
            st.switch_page("pages/3_Risk.py")
    
    with col2:
        if st.button("🎯\n\n**Optimize**", use_container_width=True, key="optimize_btn"):
            st.session_state['action'] = 'optimization'
            st.switch_page("pages/4_Copilot.py")
    
    with col3:
        if st.button("➕\n\n**Add**", use_container_width=True, key="add_btn"):
            st.switch_page("pages/2_Portfolio.py")
    
    # Stress Scenarios (iOS style horizontal scroll)
    st.markdown('<div class="section-header"><div class="section-title">Stress Scenarios</div></div>', unsafe_allow_html=True)
    
    scenarios = [
        {"name": "2008 Crisis", "loss": -37, "icon": "🔥", "color": "#ef4444"},
        {"name": "COVID 2020", "loss": -34, "icon": "🌊", "color": "#f97316"},
        {"name": "Correction", "loss": -20, "icon": "⚡", "color": "#f59e0b"},
        {"name": "Flash Crash", "loss": -9, "icon": "💨", "color": "#84cc16"}
    ]
    
    # Create horizontal scrolling cards
    cols = st.columns(len(scenarios))
    for idx, scenario in enumerate(scenarios):
        with cols[idx]:
            st.markdown(f"""
            <div class="scenario-card" style="--border-color: {scenario['color']}; --text-color: {scenario['color']};">
                <div class="scenario-icon">{scenario['icon']}</div>
                <div class="scenario-loss">{scenario['loss']}%</div>
                <div class="scenario-name">{scenario['name']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if st.button("See Full Risk Analysis →", use_container_width=True, type="secondary"):
        st.switch_page("pages/3_Risk.py")
    
    # Holdings List (iOS style)
    st.markdown('<div class="section-header"><div class="section-title">Holdings</div><div class="section-action">Edit</div></div>', unsafe_allow_html=True)
    
    # Simulate holdings data (in production, this would come from your API)
    holdings_data = []
    for i, (symbol, weight) in enumerate(zip(symbols, weights if weights else [1/len(symbols)]*len(symbols))):
        # You would fetch real prices/changes from your API
        holdings_data.append({
            'symbol': symbol,
            'weight': weight * 100,
            'price': [178.23, 378.91, 139.67, 495.22][i % 4],
            'change': [2.34, -1.12, 0.89, 4.56][i % 4]
        })
    
    st.markdown('<div class="holdings-container">', unsafe_allow_html=True)
    
    for holding in holdings_data:
        change_class = "change-positive" if holding['change'] >= 0 else "change-negative"
        change_sign = "+" if holding['change'] >= 0 else ""
        
        col1, col2, col3, col4 = st.columns([1, 3, 2, 0.5])
        
        with col1:
            st.markdown(f"""
            <div class="holding-avatar">{holding['symbol'][0]}</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="holding-info">
                <div class="holding-symbol">{holding['symbol']}</div>
                <div class="holding-weight">{holding['weight']:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="holding-price">
                <div class="holding-price-value">${holding['price']:.2f}</div>
                <div class="holding-change {change_class}">{change_sign}{holding['change']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("›", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("View Full Portfolio →", use_container_width=True, type="secondary"):
        st.switch_page("pages/2_Portfolio.py")

else:
    # Empty state with example portfolios
    st.markdown("""
    <div class="portfolio-hero">
        <div class="portfolio-value" style="font-size: 2rem;">👋 Welcome</div>
        <div style="margin-top: 1rem; opacity: 0.9;">Get started by creating your portfolio</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Try an Example Portfolio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">Balanced</div>
            <div style="font-size: 0.75rem; color: #6b7280;">60% Stocks, 40% Bonds</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Balanced", use_container_width=True, key="balanced"):
            st.session_state.portfolio = {
                'symbols': ['VTI', 'BND', 'VEA', 'GLD'],
                'weights': [0.40, 0.30, 0.20, 0.10]
            }
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💻</div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">Tech Focus</div>
            <div style="font-size: 0.75rem; color: #6b7280;">Big Tech Giants</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Tech", use_container_width=True, key="tech"):
            st.session_state.portfolio = {
                'symbols': ['AAPL', 'MSFT', 'GOOGL', 'NVDA'],
                'weights': [0.25, 0.25, 0.25, 0.25]
            }
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🚀</div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">Growth</div>
            <div style="font-size: 0.75rem; color: #6b7280;">High-growth stocks</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Growth", use_container_width=True, key="growth"):
            st.session_state.portfolio = {
                'symbols': ['TSLA', 'NVDA', 'SHOP', 'SQ'],
                'weights': [0.30, 0.30, 0.20, 0.20]
            }
            st.rerun()
    
    with col4:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">Defensive</div>
            <div style="font-size: 0.75rem; color: #6b7280;">Low volatility</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Load Defensive", use_container_width=True, key="defensive"):
            st.session_state.portfolio = {
                'symbols': ['KO', 'PG', 'JNJ', 'VZ'],
                'weights': [0.25, 0.25, 0.25, 0.25]
            }
            st.rerun()

st.markdown("---")

# Bottom Tab Bar (iOS style)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="text-align: center; color: #3b82f6;">
        <div style="font-size: 1.5rem;">🏠</div>
        <div style="font-size: 0.625rem; font-weight: 500; margin-top: 0.25rem;">Home</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("💼\n\nPortfolio", use_container_width=True, key="tab_portfolio"):
        st.switch_page("pages/2_Portfolio.py")

with col3:
    if st.button("🔥\n\nRisk", use_container_width=True, key="tab_risk"):
        st.switch_page("pages/3_Risk.py")

with col4:
    if st.button("🤖\n\nAsk", use_container_width=True, key="tab_copilot"):
        st.switch_page("pages/4_Copilot.py")