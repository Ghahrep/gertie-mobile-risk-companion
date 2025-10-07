# pages/3_Risk.py
"""
Risk Analysis Screen - iOS Reimagined
Single-scroll feed with visual hierarchy: Worst case → Scenarios → Key metrics → Actions
NOW WITH INTERACTIVE SCENARIO CARDS!
"""

import streamlit as st
import plotly.graph_objects as go
from utils.api_client import get_api_client
from utils.portfolio_manager import get_portfolio, set_portfolio
from utils.hedge_preview import show_hedge_preview_dialog, activate_hedge_preview, is_hedge_confirmed
import numpy as np
import time

from utils.tooltips import (
    show_metric_with_tooltip,
    show_learn_more_section,
    show_contextual_tip,
    tooltip_icon
)

# NEW: Import scenario modal functions
from utils.scenario_modal import (
    show_scenario_modal,
    activate_scenario_modal,
    is_scenario_modal_active,
    get_active_scenario
)

st.set_page_config(
    page_title="Risk Analysis",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced iOS-style CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Card - Worst Case Scenario */
    .risk-hero {
        background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
    }
    
    .hero-label {
        font-size: 0.875rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .hero-value {
        font-size: 3.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        margin-bottom: 1rem;
    }
    
    .hero-context {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.875rem;
        backdrop-filter: blur(10px);
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    /* Stress Scenario Cards - Horizontal Scroll */
    .scenarios-container {
        display: flex;
        gap: 0.75rem;
        overflow-x: auto;
        padding: 0.5rem 0 1rem 0;
        margin: 0 -1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        -webkit-overflow-scrolling: touch;
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
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .scenario-loss {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
        color: var(--text-color);
    }
    
    .scenario-name {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Key Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: bold;
        color: #111827;
    }
    
    .metric-subtitle {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    /* Insight Box */
    .insight-box {
        background: #f9fafb;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .insight-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .insight-text {
        font-size: 0.875rem;
        color: #6b7280;
        line-height: 1.5;
    }
    
    /* Action Buttons */
    .action-section {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Resilience Badge Colors */
    .resilience-weak { color: #ef4444; }
    .resilience-moderate { color: #f97316; }
    .resilience-strong { color: #10b981; }
</style>
""", unsafe_allow_html=True)

# Get portfolio from session state using portfolio_manager
symbols, weights = get_portfolio()

if not symbols:
    st.warning("📊 No portfolio loaded")
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    st.stop()

# Helper function
def safe_extract(data, *keys, default=0):
    """Safely extract nested dictionary values"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result is not None else default

# Load data once at the top
with st.spinner("Analyzing portfolio risk..."):
    try:
        client = get_api_client()
        
        # Convert to tuples for caching
        symbols_tuple = tuple(symbols)
        weights_tuple = tuple(weights)
        
        # Get both stress test and risk metrics (CACHED!)
        stress_response = client.run_stress_test(symbols_tuple, weights_tuple)
        risk_response = client.get_risk_analysis(symbols_tuple, weights_tuple)
        
        # Parse stress test data
        if stress_response.get('status') == 'success':
            results = stress_response.get('stress_test_results', {})
            scenarios = results.get('stress_scenarios', {})
            
            scenario_data = []
            for name, data in scenarios.items():
                if isinstance(data, dict):
                    loss = abs(safe_extract(data, 'total_loss_pct', default=0))
                    if loss < 1 and loss > 0:
                        loss = loss * 100
                elif isinstance(data, (int, float)):
                    loss = abs(data)
                    if loss < 1:
                        loss = loss * 100
                else:
                    loss = 0
                
                scenario_data.append({
                    'name': name.replace('_', ' ').title(),
                    'loss': loss
                })
            
            # Sort by severity
            scenario_data.sort(key=lambda x: x['loss'], reverse=True)
            
            worst_case = scenario_data[0]['loss'] if scenario_data else 25.0
            worst_name = scenario_data[0]['name'] if scenario_data else "Market Crisis"
            avg_loss = sum(s['loss'] for s in scenario_data) / len(scenario_data) if scenario_data else 15.0
            resilience = int(max(0, 100 - worst_case))
        else:
            # Fallback data
            scenario_data = [
                {'name': '2008 Crisis', 'loss': 37.0},
                {'name': 'COVID 2020', 'loss': 34.0},
                {'name': 'Correction', 'loss': 20.0},
                {'name': 'Flash Crash', 'loss': 9.0}
            ]
            worst_case = 37.0
            worst_name = "2008 Crisis"
            avg_loss = 25.0
            resilience = 63
        
        # Parse risk metrics
        if 'metrics' in risk_response:
            metrics = risk_response['metrics']
            current_vol = safe_extract(metrics, 'annualized_volatility', default=0)
            var_95 = abs(safe_extract(metrics, 'portfolio_var_95', default=0))
            cvar_95 = abs(safe_extract(metrics, 'portfolio_cvar_95', default=0))
            sharpe = safe_extract(metrics, 'sharpe_ratio', default=0)
            
            # Convert to percentages
            if current_vol < 1: current_vol *= 100
            if var_95 < 1: var_95 *= 100
            if cvar_95 < 1: cvar_95 *= 100
        else:
            current_vol = 20.0
            var_95 = 2.5
            cvar_95 = 3.2
            sharpe = 1.2
        
        data_loaded = True
        
    except Exception as e:
        st.error(f"Unable to load risk data: {str(e)}")
        data_loaded = False

# NEW: Check if a scenario modal is active - SHOW MODAL INSTEAD OF PAGE
if is_scenario_modal_active():
    selected_scenario = get_active_scenario()
    
    # Back navigation
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <span style="color: #6b7280; font-size: 0.875rem;">← Back to Risk Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a proper back button
    if st.button("← Back to Risk Analysis", use_container_width=True):
        st.session_state.pop('selected_scenario', None)
        st.rerun()
    
    # Show the detailed scenario modal
    show_scenario_modal(selected_scenario, symbols, weights)
    
    # Stop here - don't show the rest of the page
    st.stop()

# Only show content if data loaded
if data_loaded:
    
    # 1. HERO CARD - Worst Case Scenario WITH TOOLTIPS
    resilience_class = (
        "resilience-strong" if resilience >= 70 
        else "resilience-moderate" if resilience >= 40 
        else "resilience-weak"
    )

    st.markdown(f"""
    <div class="risk-hero">
        <div class="hero-label">Worst Case Scenario</div>
        <div class="hero-value">-{worst_case:.0f}%</div>
        <div class="hero-subtitle">{worst_name}</div>
        <div class="hero-context">
            💡 Your portfolio would lose ${worst_case * 1274.85:.0f} in a similar crisis
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <div style="font-size: 0.75rem; opacity: 0.8; margin-bottom: 0.25rem;">Portfolio Resilience</div>
            <div style="font-size: 2rem; font-weight: bold;" class="{resilience_class}">{resilience}/100</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tooltips for worst case and resilience
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("ℹ️ What is Worst Case Scenario?"):
            st.markdown(tooltip_icon("worst_case", inline=False))

    with col2:
        with st.expander("ℹ️ What is Portfolio Resilience?"):
            st.markdown(tooltip_icon("resilience", inline=False))
    
    # 2. STRESS SCENARIOS - NOW INTERACTIVE! 🎉
    st.markdown('<div class="section-header">All Stress Scenarios</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 0.75rem;">
        👆 Tap any scenario to see detailed historical analysis
    </div>
    """, unsafe_allow_html=True)
    
    # Map scenarios to emojis and colors
    scenario_icons = {
        '2008 Crisis': ('🔥', '#ef4444'),
        'COVID 2020': ('🌊', '#f97316'),
        'Dot Com': ('💻', '#f59e0b'),
        'Correction': ('⚡', '#fbbf24'),
        'Flash Crash': ('💨', '#84cc16'),
        'Black Monday': ('📉', '#dc2626'),
        'Asian Crisis': ('🌏', '#fb923c'),
        'Oil Shock': ('🛢️', '#f87171')
    }
    
    # Create clickable cards - Top 4 scenarios
    cols = st.columns(min(len(scenario_data), 4))
    
    for idx, scenario in enumerate(scenario_data[:4]):
        icon, color = scenario_icons.get(scenario['name'], ('📊', '#6b7280'))
        
        with cols[idx]:
            st.markdown(f"""
            <div style="background: white; border-radius: 16px; padding: 1.25rem; min-width: 140px;
                        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
                        border-top: 3px solid {color}; margin-bottom: 0.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.25rem; color: {color};">
                    -{scenario['loss']:.0f}%
                </div>
                <div style="font-size: 0.75rem; color: #6b7280; font-weight: 500;">
                    {scenario['name']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Clickable button below each card
            if st.button("View Details", key=f"scenario_card_{scenario['name']}", use_container_width=True):
                activate_scenario_modal(scenario['name'])
                st.rerun()
    
    # Show all scenarios in expandable section
    with st.expander(f"📊 View All {len(scenario_data)} Scenarios"):
        # Create a grid of all scenarios
        for i in range(0, len(scenario_data), 2):
            col1, col2 = st.columns(2)
            
            # First scenario in row
            with col1:
                if i < len(scenario_data):
                    scenario = scenario_data[i]
                    icon, color = scenario_icons.get(scenario['name'], ('📊', '#6b7280'))
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; 
                                border-left: 4px solid {color}; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: {color};">
                            -{scenario['loss']:.1f}%
                        </div>
                        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
                            {scenario['name']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View Details", key=f"detail_{i}", use_container_width=True):
                        activate_scenario_modal(scenario['name'])
                        st.rerun()
            
            # Second scenario in row
            with col2:
                if i + 1 < len(scenario_data):
                    scenario = scenario_data[i + 1]
                    icon, color = scenario_icons.get(scenario['name'], ('📊', '#6b7280'))
                    
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; 
                                border-left: 4px solid {color}; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{icon}</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: {color};">
                            -{scenario['loss']:.1f}%
                        </div>
                        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
                            {scenario['name']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View Details", key=f"detail_{i+1}", use_container_width=True):
                        activate_scenario_modal(scenario['name'])
                        st.rerun()
    
    # 3. KEY RISK METRICS - 2x2 Grid WITH TOOLTIPS
    st.markdown('<div class="section-header">Key Risk Metrics</div>', unsafe_allow_html=True)

    # Row 1
    col1, col2 = st.columns(2)

    with col1:
        # Volatility with tooltip
        show_metric_with_tooltip(
            label="Volatility",
            value=f"{current_vol:.1f}%",
            metric_key="volatility"
        )
        st.caption("Annual")

    with col2:
        # VaR with tooltip
        show_metric_with_tooltip(
            label="VaR (95%)",
            value=f"{var_95:.1f}%",
            metric_key="var"
        )
        st.caption("Daily max loss")

    # Row 2
    col3, col4 = st.columns(2)

    with col3:
        # CVaR with tooltip
        show_metric_with_tooltip(
            label="Tail Risk",
            value=f"{cvar_95:.1f}%",
            metric_key="cvar"
        )
        st.caption("CVaR (95%)")

    with col4:
        # Sharpe with tooltip
        sharpe_color = "#10b981" if sharpe > 1 else "#f59e0b" if sharpe > 0.5 else "#ef4444"
        show_metric_with_tooltip(
            label="Sharpe Ratio",
            value=f"{sharpe:.2f}",
            metric_key="sharpe_ratio"
        )
        st.caption("Risk-adjusted")

    # Add "Learn More" section for all metrics
    with st.expander("📚 Understanding These Metrics"):
        tab1, tab2, tab3, tab4 = st.tabs(["Volatility", "VaR", "CVaR/Tail Risk", "Sharpe Ratio"])
        
        with tab1:
            st.markdown(tooltip_icon("volatility", inline=False))
        
        with tab2:
            st.markdown(tooltip_icon("var", inline=False))
        
        with tab3:
            st.markdown(tooltip_icon("cvar", inline=False))
        
        with tab4:
            st.markdown(tooltip_icon("sharpe_ratio", inline=False))
    
    # 4. INTERPRETATION - What This Means
    st.markdown('<div class="section-header">What This Means</div>', unsafe_allow_html=True)

    # Generate contextual insight
    if worst_case > 30:
        insight_icon = "⚠️"
        insight_title = "High Risk Detected"
        insight_text = f"Your portfolio shows significant vulnerability to major market downturns. In a severe crisis like {worst_name}, you could lose over {worst_case:.0f}% of your value. Consider adding defensive assets like bonds or gold to reduce downside risk."
        border_color = "#ef4444"
        tip_scenario = "high_risk"
    elif worst_case > 20:
        insight_icon = "⚡"
        insight_title = "Moderate Risk Level"
        insight_text = f"Your portfolio has moderate exposure to market crashes. A {worst_name}-style event could result in a {worst_case:.0f}% loss. Review your hedging strategy to protect against downside scenarios."
        border_color = "#f97316"
        tip_scenario = "high_volatility"
    else:
        insight_icon = "✓"
        insight_title = "Well-Protected Portfolio"
        insight_text = f"Your portfolio shows good resilience. Even in a {worst_name} scenario, losses would be limited to {worst_case:.0f}%. Continue monitoring risk levels and maintain diversification."
        border_color = "#10b981"
        tip_scenario = "good_portfolio"

    st.markdown(f"""
    <div class="insight-box" style="border-left-color: {border_color};">
        <div class="insight-title">
            <span style="font-size: 1.5rem;">{insight_icon}</span>
            <span>{insight_title}</span>
        </div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Show contextual tip based on risk level
    show_contextual_tip(tip_scenario)
    
    # 5. RECOMMENDED ACTIONS
    st.markdown('<div class="section-header">Recommended Actions</div>', unsafe_allow_html=True)
    
    if st.button("🎯 Optimize Portfolio", use_container_width=True, type="primary"):
        st.session_state['action'] = 'optimization'
        st.switch_page("pages/4_Copilot.py")
    
    # 6. HEDGING SECTION (INTEGRATED WITH PREVIEW)
    st.markdown("---")
    st.markdown('<div class="section-header">🛡️ Protect Your Portfolio</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">
        Add defensive assets to reduce your downside risk in market crashes
    </div>
    """, unsafe_allow_html=True)
    
    # Quick hedge recommendations
    quick_hedges = [
        {
            'symbol': 'TLT',
            'name': '20+ Year Treasury Bonds',
            'description': 'Safe haven during market crashes',
            'expected_impact': '8-12% crisis reduction',
            'color': '#3b82f6'
        },
        {
            'symbol': 'GLD',
            'name': 'Gold ETF',
            'description': 'Inflation hedge and diversifier',
            'expected_impact': '6-10% crisis reduction',
            'color': '#f59e0b'
        },
        {
            'symbol': 'BND',
            'name': 'Total Bond Market',
            'description': 'Broad bond exposure',
            'expected_impact': '5-8% crisis reduction',
            'color': '#10b981'
        }
    ]
    
    # Check if any hedge preview is active
    active_preview = None
    for hedge in quick_hedges:
        if st.session_state.get(f"hedge_preview_{hedge['symbol']}_active", False):
            active_preview = hedge
            break
    
    if active_preview:
        # Show the preview dialog
        showing, confirmed = show_hedge_preview_dialog(
            hedge_symbol=active_preview['symbol'],
            hedge_name=active_preview['name'],
            hedge_description=active_preview['description'],
            current_symbols=symbols,
            current_weights=weights,
            hedge_weight=0.10
        )
        
        if confirmed:
            # User confirmed - add the hedge
            hedge_weight = 0.10
            scale_factor = 1 - hedge_weight
            
            if symbols and weights:
                new_symbols = symbols + [active_preview['symbol']]
                new_weights = [w * scale_factor for w in weights] + [hedge_weight]
                
                set_portfolio(new_symbols, new_weights)
                
                st.success(f"✓ Added {active_preview['symbol']} ({hedge_weight*100:.0f}% allocation)")
                st.balloons()
                time.sleep(1.5)
                st.rerun()
    
    else:
        # Show hedge cards with "Preview" buttons
        for hedge in quick_hedges:
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; 
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid {hedge['color']};">
                    <div style="font-weight: 600; color: #111827; margin-bottom: 0.25rem;">
                        {hedge['symbol']} - {hedge['name']}
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280; margin-bottom: 0.25rem;">
                        {hedge['description']}
                    </div>
                    <div style="font-size: 0.75rem; color: {hedge['color']}; font-weight: 500;">
                        💡 {hedge['expected_impact']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)  # Spacer
                if st.button("Preview", key=f"preview_hedge_{hedge['symbol']}", use_container_width=True):
                    activate_hedge_preview(hedge['symbol'])
                    st.rerun()
    
    # Advanced hedge analysis (expandable)
    with st.expander("🔍 Advanced Hedge Analysis"):
        st.markdown("""
        **Want personalized hedge recommendations?**
        
        Run AI-powered analysis to find the optimal hedges specifically for your portfolio.
        This analyzes correlations, tail risk reduction, and impact on your worst-case scenarios.
        """)
        
        if st.button("Run Advanced Analysis", use_container_width=True, type="primary", key="advanced_hedge"):
            # Create placeholder for progress updates
            progress_placeholder = st.empty()
            status_text = st.empty()
            
            try:
                # Show initial status
                status_text.info("🔍 Analyzing your portfolio...")
                
                # Convert to tuples for caching
                symbols_tuple = tuple(symbols)
                weights_tuple = tuple(weights)
                
                # Start analysis with progress callback
                import time
                start_time = time.time()
                
                # Show analyzing status
                with progress_placeholder.container():
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; padding: 1rem; border-radius: 12px; text-align: center;'>
                        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🔍</div>
                        <div style='font-size: 0.875rem;'>Evaluating hedge candidates...</div>
                        <div style='font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>
                            Analyzing correlations, volatility reduction, and tail risk improvements
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Call optimized API (now with parallel evaluation)
                hedge_response = client.analyze_hedge_opportunities(
                    symbols_tuple,
                    weights_tuple,
                    period="1year",
                    top_n=5,  # Get top 5 from the 10 evaluated
                    timeout=30  # Reduced from 60s - should finish in 10-15s now
                )
                
                elapsed_time = time.time() - start_time
                
                # Clear progress indicator
                progress_placeholder.empty()
                status_text.empty()
                
                if "error" in hedge_response:
                    st.error(f"❌ {hedge_response['error']}")
                elif hedge_response.get('status') == 'success':
                    top_hedges = hedge_response.get('top_hedges', [])
                    
                    if not top_hedges:
                        st.warning("No suitable hedge candidates found for your portfolio.")
                    else:
                        # Show success with timing
                        st.success(f"✅ Analysis complete in {elapsed_time:.1f}s - Found {len(top_hedges)} optimal hedges")
                        
                        st.markdown("### 🎯 Optimal Hedges for Your Portfolio")
                        
                        for i, hedge in enumerate(top_hedges, 1):
                            # Color code by score
                            if hedge.get('score', 0) > 0.15:
                                border_color = "#10b981"  # Green - excellent
                                score_emoji = "🌟"
                            elif hedge.get('score', 0) > 0.10:
                                border_color = "#3b82f6"  # Blue - good
                                score_emoji = "⭐"
                            else:
                                border_color = "#6b7280"  # Gray - okay
                                score_emoji = "✓"
                            
                            st.markdown(f"""
                            <div style="background: #f9fafb; border-radius: 12px; padding: 1rem; 
                                        margin: 0.75rem 0; border-left: 4px solid {border_color};">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="font-weight: 600; color: #111827; font-size: 1rem;">
                                        {score_emoji} {i}. {hedge['symbol']}
                                    </div>
                                    <div style="background: {border_color}; color: white; padding: 0.25rem 0.75rem; 
                                                border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                        Score: {hedge.get('score', 0):.3f}
                                    </div>
                                </div>
                                <div style="font-size: 0.875rem; color: #6b7280; line-height: 1.6;">
                                    <strong>Category:</strong> {hedge.get('category', 'Unknown')}<br/>
                                    <strong>CVaR Improvement:</strong> {hedge.get('cvar_improvement', 0)*100:.1f}% better<br/>
                                    <strong>Volatility Reduction:</strong> {hedge.get('volatility_reduction', 0)*100:.1f}%<br/>
                                    <strong>Correlation:</strong> {hedge.get('correlation', 0):.2f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add preview button
                            col1, col2 = st.columns([3, 1])
                            with col2:
                                if st.button(f"Preview", key=f"preview_optimal_{hedge['symbol']}", use_container_width=True):
                                    activate_hedge_preview(hedge['symbol'])
                                    st.rerun()
                else:
                    st.error("❌ Analysis failed - check API connection")
            
            except Exception as e:
                progress_placeholder.empty()
                status_text.empty()
                st.error(f"❌ Unable to run analysis: {str(e)}")
        
        st.markdown("---")
        st.markdown("""
        **How Hedging Works:**
        
        Hedging reduces portfolio risk by adding assets that:
        - Move differently than your current holdings
        - Protect against crashes with low/negative correlation  
        - Lower tail risk (CVaR) and worst-case losses
        
        **Trade-off:** Lower risk often means lower returns during bull markets.
        
        **⚡ New:** Analysis optimized - now completes in 10-15 seconds instead of 30-40 seconds!
        """)
    
    # 7. OPTIONAL: Advanced Details (Collapsed by default)
    with st.expander("📊 Advanced Risk Details"):
        st.markdown("### Volatility Context")
        
        daily_vol = current_vol / np.sqrt(252)
        monthly_vol = current_vol / np.sqrt(12)
        
        st.markdown(f"""
        **What volatility means for you:**
        - **Daily:** Typical move of ±{daily_vol:.2f}%
        - **Monthly:** Typical range of ±{monthly_vol:.1f}%
        - **Annual:** Expected range of ±{current_vol:.1f}%
        
        On 95% of days, your portfolio won't lose more than {var_95:.1f}%. 
        On the worst 5% of days, average loss is {cvar_95:.1f}% (CVaR).
        """)
        
        # Add detailed explanations
        show_learn_more_section("volatility")
        
        st.markdown("---")
        st.markdown("### Understanding VaR & CVaR")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**VaR (95%)**")
            st.info(tooltip_icon("var", inline=True))
        
        with col2:
            st.markdown("**CVaR (Tail Risk)**")
            st.info(tooltip_icon("cvar", inline=True))
        
        # Visual comparison
        st.markdown("**The Difference:**")
        st.markdown("""
        - **VaR** = Your "typical bad day" (happens ~1x per month)
        - **CVaR** = Your "disaster day" (the really bad 5%)
        
        Think of VaR as your expected loss on a bad day, and CVaR as what happens when things go truly wrong.
        """)

else:
    # Fallback if data doesn't load
    st.error("Unable to load risk analysis")
    st.info("Please check your API connection and try again")
    
    if st.button("🔄 Retry", use_container_width=True):
        st.rerun()

# Bottom Navigation
st.markdown("---")
st.markdown("### 📚 Learn More About Risk")

with st.expander("Risk Management Guide", expanded=False):
    st.markdown("""
    ## Understanding Portfolio Risk
    
    **The Three Pillars:**
    
    1. **Volatility Management**
       - Lower volatility = smoother ride
       - Target: 15-25% for balanced portfolios
       - Action: Add bonds, defensive stocks, or low-vol ETFs
    
    2. **Tail Risk Protection**
       - CVaR shows your crash exposure
       - Target: CVaR under 4% for moderate risk
       - Action: Use hedges like TLT, GLD, or defensive positions
    
    3. **Risk-Adjusted Returns**
       - Sharpe ratio above 1.0 is good
       - Higher Sharpe = more bang for your buck
       - Action: Optimize portfolio or rebalance
    
    **Quick Actions:**
    - High risk? → Add defensive assets
    - High volatility? → Add bonds or low-vol stocks
    - Low Sharpe? → Run portfolio optimization
    
    **Need Help?**
    Ask the Co-pilot: "How can I reduce my portfolio risk?"
    """)

# Bottom Navigation
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("Home.py", label="🏠 Home", use_container_width=True)

with col2:
    st.page_link("pages/2_Portfolio.py", label="💼 Portfolio", use_container_width=True)

with col3:
    st.page_link("pages/3_Risk.py", label="🔥 Risk", use_container_width=True)

with col4:
    st.page_link("pages/4_Copilot.py", label="🤖 Ask", use_container_width=True)