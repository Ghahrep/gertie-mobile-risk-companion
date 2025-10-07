# pages/4_Copilot.py
"""
AI Co-pilot - Smart Suggestions
Button-based interaction with contextual insights
"""

import streamlit as st
from utils.api_client import get_api_client
from utils.portfolio_manager import get_portfolio  # ADDED
from utils.agent import process_query
import time

st.set_page_config(
    page_title="Co-pilot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# iOS-inspired CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Section */
    .copilot-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .hero-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .hero-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .hero-subtitle {
        font-size: 0.875rem;
        opacity: 0.9;
    }
    
    /* Insight Card */
    .insight-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    .insight-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .insight-icon {
        font-size: 1.5rem;
    }
    
    .insight-title {
        font-weight: 600;
        color: #111827;
        font-size: 1rem;
    }
    
    .insight-text {
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }
    
    /* Question Button */
    .question-btn {
        background: #f9fafb;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
    }
    
    .question-btn:hover {
        border-color: #667eea;
        background: #f3f4f6;
    }
    
    .question-text {
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    
    .question-preview {
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    /* Section Header */
    .section-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    /* Response Card */
    .response-card {
        background: #f9fafb;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    .response-text {
        color: #374151;
        font-size: 0.875rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Get portfolio from session state using portfolio_manager
symbols, weights = get_portfolio()  # FIXED
portfolio_loaded = bool(symbols)

if not portfolio_loaded:
    st.markdown("""
    <div class="copilot-hero">
        <div class="hero-icon">🤖</div>
        <div class="hero-title">AI Co-pilot</div>
        <div class="hero-subtitle">Load a portfolio to get started</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go Home", use_container_width=True, type="primary"):
            st.switch_page("Home.py")
    with col2:
        if st.button("💼 Load Portfolio", use_container_width=True):
            st.switch_page("pages/2_Portfolio.py")
    st.stop()

# Hero Section
st.markdown("""
<div class="copilot-hero">
    <div class="hero-icon">🤖</div>
    <div class="hero-title">Your AI Co-pilot</div>
    <div class="hero-subtitle">Personalized insights for your portfolio</div>
</div>
""", unsafe_allow_html=True)

# Check for pending actions from other pages
if 'action' in st.session_state:
    action = st.session_state.pop('action')
    st.session_state['show_response'] = action

# Display response if there's a pending action
if 'show_response' in st.session_state:
    action = st.session_state.pop('show_response')
    
    st.markdown('<div class="section-header">💡 Analysis</div>', unsafe_allow_html=True)
    
    with st.spinner("Analyzing..."):
        # Map actions to queries
        action_map = {
            'optimization': "How can I optimize my portfolio to maximize Sharpe ratio?",
            'hedging': "What are the best hedges for my portfolio?",
            'stress_test': "Run a comprehensive stress test on my portfolio",
            'correlation': "Show me the correlations in my portfolio"
        }
        
        query = action_map.get(action, action)
        response = process_query(query)
        
        st.markdown(f"""
        <div class="response-card">
            <div class="response-text">{response.get('text', 'Analysis complete. See recommendations below.')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show action buttons if available
        if response.get('actions'):
            st.markdown("---")
            cols = st.columns(len(response['actions'][:3]))
            for i, action_btn in enumerate(response['actions'][:3]):
                with cols[i]:
                    if st.button(action_btn['label'], use_container_width=True, key=f"action_{i}"):
                        st.session_state['show_response'] = action_btn.get('target', '')
                        st.rerun()

# Generate smart insights based on portfolio
st.markdown('<div class="section-header">📊 Key Insights</div>', unsafe_allow_html=True)

# Load portfolio risk data for contextual insights
try:
    client = get_api_client()
    
    # Convert to tuples for caching
    symbols_tuple = tuple(symbols)
    weights_tuple = tuple(weights)
    risk_response = client.get_risk_analysis(symbols_tuple, weights_tuple)  # FIXED
    
    if 'metrics' in risk_response:
        metrics = risk_response['metrics']
        vol = metrics.get('annualized_volatility', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        
        if vol < 1: vol *= 100
        
        # Generate contextual insights
        insights = []
        
        # Volatility insight
        if vol > 25:
            insights.append({
                'icon': '⚡',
                'title': 'High Volatility Detected',
                'text': f'Your portfolio volatility is {vol:.1f}%, which is higher than average. This means larger daily swings in value.',
                'action': 'reduce_volatility'
            })
        elif vol < 15:
            insights.append({
                'icon': '✓',
                'title': 'Low Volatility',
                'text': f'Your portfolio volatility is {vol:.1f}%, indicating stable, predictable returns.',
                'action': None
            })
        
        # Sharpe ratio insight
        if sharpe < 0.5:
            insights.append({
                'icon': '⚠️',
                'title': 'Poor Risk-Adjusted Returns',
                'text': f'Your Sharpe ratio is {sharpe:.2f}, suggesting you are not being adequately compensated for risk.',
                'action': 'optimization'
            })
        elif sharpe > 1.5:
            insights.append({
                'icon': '🎯',
                'title': 'Excellent Risk-Adjusted Returns',
                'text': f'Your Sharpe ratio of {sharpe:.2f} indicates strong risk-adjusted performance.',
                'action': None
            })
        
        # Concentration insight
        if weights:
            max_weight = max(weights)
            if max_weight > 0.35:
                max_idx = weights.index(max_weight)
                insights.append({
                    'icon': '📊',
                    'title': 'Concentration Risk',
                    'text': f'{symbols[max_idx]} represents {max_weight*100:.0f}% of your portfolio. This increases concentration risk.',
                    'action': 'diversification'
                })
        
        # Display insights
        for insight in insights:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-header">
                    <div class="insight-icon">{insight['icon']}</div>
                    <div class="insight-title">{insight['title']}</div>
                </div>
                <div class="insight-text">{insight['text']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if insight['action']:
                if st.button(f"Learn More →", key=f"insight_{insight['action']}", use_container_width=True):
                    st.session_state['show_response'] = insight['action']
                    st.rerun()

except Exception as e:
    st.info("💡 Load portfolio data to see personalized insights")

# Smart Questions Section
st.markdown('<div class="section-header">❓ Common Questions</div>', unsafe_allow_html=True)

questions = [
    {
        'q': 'How can I reduce my portfolio risk?',
        'preview': 'Get recommendations for hedges and optimization',
        'action': 'reduce_risk'
    },
    {
        'q': 'What is my worst-case scenario?',
        'preview': 'See stress test results and crisis impacts',
        'action': 'stress_test'
    },
    {
        'q': 'How should I rebalance?',
        'preview': 'Optimize allocation for better risk-adjusted returns',
        'action': 'optimization'
    },
    {
        'q': 'Are my holdings too correlated?',
        'preview': 'Analyze diversification and correlation matrix',
        'action': 'correlation'
    },
    {
        'q': 'What hedges should I add?',
        'preview': 'Find assets that reduce downside risk',
        'action': 'hedging'
    }
]

for i, q in enumerate(questions):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown(f"""
        <div class="question-btn">
            <div class="question-text">{q['q']}</div>
            <div class="question-preview">{q['preview']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("→", key=f"q_{i}", use_container_width=True):
            st.session_state['show_response'] = q['action']
            st.rerun()

# Quick Actions
st.markdown("---")
st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯\n\nOptimize", use_container_width=True):
        st.session_state['show_response'] = 'optimization'
        st.rerun()

with col2:
    if st.button("🛡️\n\nHedge", use_container_width=True):
        st.session_state['show_response'] = 'hedging'
        st.rerun()

with col3:
    if st.button("🔥\n\nRisk", use_container_width=True):
        st.switch_page("pages/3_Risk.py")

# Still want to chat?
with st.expander("💬 Ask a Custom Question"):
    st.markdown("""
    **Prefer to type your own question?**
    
    While the buttons above cover most common needs, you can also ask specific questions:
    """)
    
    custom_query = st.text_input("Your question:", placeholder="e.g., Should I add more tech stocks?")
    
    if st.button("Ask", use_container_width=True) and custom_query:
        with st.spinner("Thinking..."):
            response = process_query(custom_query)
            
            response_text = response.get('text', 'Here is what I found...')
            st.markdown(f"""
            <div class="response-card">
                <div class="response-text">{response_text}</div>
            </div>
            """, unsafe_allow_html=True)


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