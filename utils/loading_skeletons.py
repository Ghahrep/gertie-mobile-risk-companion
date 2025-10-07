# utils/loading_skeletons.py
"""
Loading skeleton components for better perceived performance
Shows structure while data is loading instead of blank screens
"""

import streamlit as st

def show_metric_skeleton(label: str = "Loading..."):
    """Show skeleton for a metric card"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    ">
        <div style="color: #666; font-size: 0.875rem; margin-bottom: 0.5rem;">{label}</div>
        <div style="
            background: #e0e2e6;
            height: 2rem;
            width: 60%;
            border-radius: 0.25rem;
        "></div>
    </div>
    <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
    </style>
    """, unsafe_allow_html=True)

def show_hero_card_skeleton():
    """Show skeleton for hero portfolio value card"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        padding: 2rem;
        color: white;
        margin: 1rem 0;
    ">
        <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">Portfolio Value</div>
        <div style="
            background: rgba(255, 255, 255, 0.3);
            height: 3rem;
            width: 50%;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        "></div>
        <div style="
            background: rgba(255, 255, 255, 0.2);
            height: 1rem;
            width: 30%;
            border-radius: 0.25rem;
        "></div>
    </div>
    """, unsafe_allow_html=True)

def show_risk_score_skeleton():
    """Show skeleton for circular risk score"""
    st.markdown("""
    <div style="
        background: #f8f9fa;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    ">
        <div style="
            background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 1rem auto;
        "></div>
        <div style="
            background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            height: 1.5rem;
            width: 60%;
            margin: 0.5rem auto;
            border-radius: 0.25rem;
        "></div>
    </div>
    <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
    </style>
    """, unsafe_allow_html=True)

def show_chart_skeleton(height: int = 400):
    """Show skeleton for chart area"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 0.5rem;
        height: {height}px;
        margin: 1rem 0;
    "></div>
    <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
    </style>
    """, unsafe_allow_html=True)

def show_insight_card_skeleton(count: int = 3):
    """Show skeleton for insight cards"""
    for i in range(count):
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e0e2e6;
            border-radius: 0.75rem;
            padding: 1.25rem;
            margin: 0.75rem 0;
        ">
            <div style="
                background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                height: 1rem;
                width: 70%;
                margin-bottom: 0.75rem;
                border-radius: 0.25rem;
            "></div>
            <div style="
                background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                height: 0.75rem;
                width: 90%;
                margin-bottom: 0.5rem;
                border-radius: 0.25rem;
            "></div>
            <div style="
                background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                height: 0.75rem;
                width: 80%;
                border-radius: 0.25rem;
            "></div>
        </div>
        <style>
            @keyframes shimmer {{
                0% {{ background-position: -200% 0; }}
                100% {{ background-position: 200% 0; }}
            }}
        </style>
        """, unsafe_allow_html=True)

def show_table_skeleton(rows: int = 5):
    """Show skeleton for data table"""
    st.markdown("""
    <style>
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    for i in range(rows):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                height: 1.5rem;
                border-radius: 0.25rem;
                margin: 0.25rem 0;
            "></div>
            """, unsafe_allow_html=True)
        
        for col in cols[1:]:
            with col:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    height: 1.5rem;
                    border-radius: 0.25rem;
                    margin: 0.25rem 0;
                "></div>
                """, unsafe_allow_html=True)

def show_scenario_cards_skeleton(count: int = 4):
    """Show skeleton for stress scenario cards"""
    cols = st.columns(min(count, 4))
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 2px solid #e0e2e6;
                border-radius: 1rem;
                padding: 1rem;
                text-align: center;
                margin: 0.5rem 0;
            ">
                <div style="
                    background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    height: 2.5rem;
                    width: 2.5rem;
                    border-radius: 50%;
                    margin: 0 auto 0.75rem auto;
                "></div>
                <div style="
                    background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    height: 1rem;
                    width: 80%;
                    margin: 0.5rem auto;
                    border-radius: 0.25rem;
                "></div>
                <div style="
                    background: linear-gradient(90deg, #f0f2f6 25%, #e0e2e6 50%, #f0f2f6 75%);
                    background-size: 200% 100%;
                    animation: shimmer 1.5s infinite;
                    height: 1.5rem;
                    width: 60%;
                    margin: 0.5rem auto;
                    border-radius: 0.25rem;
                "></div>
            </div>
            <style>
                @keyframes shimmer {{
                    0% {{ background-position: -200% 0; }}
                    100% {{ background-position: 200% 0; }}
                }}
            </style>
            """, unsafe_allow_html=True)

def show_loading_message(message: str = "Loading...", emoji: str = "⏳"):
    """Show a friendly loading message"""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem;
        color: #666;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{emoji}</div>
        <div style="font-size: 1.1rem; font-weight: 500;">{message}</div>
    </div>
    """, unsafe_allow_html=True)