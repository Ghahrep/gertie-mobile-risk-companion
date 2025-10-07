# utils/scenario_modal.py
"""
Interactive Scenario Modal
Shows detailed historical context, portfolio impact, and lessons learned
"""

import streamlit as st
import plotly.graph_objects as go
from utils.scenario_data import get_scenario_detail, estimate_portfolio_impact
from typing import List
import numpy as np


def show_scenario_modal(scenario_name: str, portfolio_symbols: List[str], portfolio_weights: List[float]):
    """
    Display detailed modal for a stress scenario
    
    Args:
        scenario_name: Name of scenario (e.g., "2008 Crisis")
        portfolio_symbols: List of ticker symbols in portfolio
        portfolio_weights: List of weights for each symbol
    """
    
    # Get scenario details from database
    detail = get_scenario_detail(scenario_name)
    
    # Calculate portfolio-specific impact
    portfolio_impacts = estimate_portfolio_impact(
        scenario_name,
        portfolio_symbols,
        portfolio_weights
    )
    
    # Modal container with enhanced styling
    st.markdown(f"""
    <style>
        .scenario-modal {{
            background: white;
            border-radius: 20px;
            padding: 0;
            margin: 1rem 0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, {detail.color} 0%, {detail.color}dd 100%);
            color: white;
            padding: 2rem 1.5rem;
            position: relative;
        }}
        
        .modal-icon {{
            font-size: 4rem;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}
        
        .modal-title {{
            font-size: 1.75rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .modal-subtitle {{
            font-size: 1rem;
            opacity: 0.95;
        }}
        
        .modal-body {{
            padding: 1.5rem;
        }}
        
        .section-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: #111827;
            margin: 1.5rem 0 0.75rem 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .timeline-stat {{
            background: #f9fafb;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #e5e7eb;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: {detail.color};
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }}
        
        .impact-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            background: #f9fafb;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}
        
        .lesson-item {{
            background: #f0f9ff;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-size: 0.875rem;
            line-height: 1.6;
        }}
    </style>
    
    <div class="scenario-modal">
        <div class="modal-header">
            <div class="modal-icon">{detail.icon}</div>
            <div class="modal-title">{detail.name}</div>
            <div class="modal-subtitle">{detail.date_range}</div>
        </div>
        <div class="modal-body">
    """, unsafe_allow_html=True)
    
    # 1. OVERVIEW
    st.markdown(f"""
    <div style="background: #fef3c7; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; border-left: 4px solid #f59e0b;">
        <strong>📊 Impact Summary:</strong><br/>
        {detail.impact_summary}
    </div>
    """, unsafe_allow_html=True)
    
    # 2. WHAT HAPPENED - Timeline
    st.markdown('<div class="section-title">📖 What Happened</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 0.875rem; color: #4b5563; line-height: 1.6; margin-bottom: 1rem;">
        {detail.description}
    </div>
    """, unsafe_allow_html=True)
    
    # Show key events as timeline
    for i, event in enumerate(detail.what_happened, 1):
        st.markdown(f"""
        <div style="display: flex; gap: 0.75rem; margin: 0.75rem 0;">
            <div style="background: {detail.color}; color: white; width: 24px; height: 24px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-size: 0.75rem; font-weight: bold; flex-shrink: 0;">
                {i}
            </div>
            <div style="font-size: 0.875rem; color: #374151; padding-top: 2px;">
                {event}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. CRISIS TIMELINE STATS
    st.markdown('<div class="section-title">⏱️ Crisis Timeline</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="timeline-stat">
            <div class="stat-value">{detail.sp500_decline*100:.0f}%</div>
            <div class="stat-label">S&P 500 Decline</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="timeline-stat">
            <div class="stat-value">{detail.duration_months}</div>
            <div class="stat-label">Months of Decline</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="timeline-stat">
            <div class="stat-value">{detail.recovery_months}</div>
            <div class="stat-label">Months to Recover</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem;">
        📅 Peak recovery: {detail.peak_recovery_date}
    </div>
    """, unsafe_allow_html=True)
    
    # 4. DRAWDOWN & RECOVERY CHART
    st.markdown('<div class="section-title">📉 Drawdown & Recovery Timeline</div>', unsafe_allow_html=True)
    
    # Create timeline visualization
    months_total = detail.duration_months + detail.recovery_months
    months = list(range(months_total + 1))
    
    # Calculate drawdown curve (exponential decay during crash, recovery after)
    portfolio_values = []
    for month in months:
        if month <= detail.duration_months:
            # During crash - exponential decay
            progress = month / detail.duration_months
            value = 100 * (1 + detail.sp500_decline * progress)
        else:
            # Recovery phase - exponential recovery
            recovery_progress = (month - detail.duration_months) / detail.recovery_months
            min_value = 100 * (1 + detail.sp500_decline)
            value = min_value + (100 - min_value) * (recovery_progress ** 0.8)
        
        portfolio_values.append(value)
    
    fig = go.Figure()
    
    # Add the drawdown/recovery line
    fig.add_trace(go.Scatter(
        x=months,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color=detail.color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba({int(detail.color[1:3], 16)}, {int(detail.color[3:5], 16)}, {int(detail.color[5:7], 16)}, 0.1)'
    ))
    
    # Add baseline at 100
    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="Starting Value", annotation_position="right")
    
    # Mark the bottom
    min_idx = detail.duration_months
    min_val = portfolio_values[min_idx]
    fig.add_trace(go.Scatter(
        x=[min_idx],
        y=[min_val],
        mode='markers+text',
        marker=dict(size=12, color=detail.color),
        text=[f"Bottom: {min_val:.0f}"],
        textposition="bottom center",
        showlegend=False
    ))
    
    fig.update_layout(
        title=f"Portfolio Value During {detail.name}",
        xaxis_title="Months",
        yaxis_title="Portfolio Value (% of starting)",
        height=350,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. YOUR PORTFOLIO IMPACT
    st.markdown('<div class="section-title">💰 Impact on Your Portfolio</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 1rem;">
        Estimated losses for each asset in your portfolio during this scenario:
    </div>
    """, unsafe_allow_html=True)
    
    # Sort by impact (worst first)
    impact_items = [(symbol, portfolio_impacts.get(symbol, detail.sp500_decline), weight) 
                    for symbol, weight in zip(portfolio_symbols, portfolio_weights)]
    impact_items.sort(key=lambda x: x[1])
    
    for symbol, impact, weight in impact_items:
        loss_pct = abs(impact * 100)
        weighted_loss = loss_pct * weight
        
        # Color based on severity
        if loss_pct > 40:
            bar_color = "#ef4444"
        elif loss_pct > 25:
            bar_color = "#f97316"
        else:
            bar_color = "#fbbf24"
        
        st.markdown(f"""
        <div class="impact-row">
            <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1;">
                <div style="font-weight: 600; color: #111827; min-width: 60px;">{symbol}</div>
                <div style="flex: 1; background: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="width: {min(loss_pct, 100)}%; height: 100%; background: {bar_color};"></div>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <div style="font-size: 0.75rem; color: #6b7280; min-width: 60px;">
                    Weight: {weight*100:.1f}%
                </div>
                <div style="font-weight: 600; color: {bar_color}; min-width: 60px; text-align: right;">
                    -{loss_pct:.1f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Total portfolio impact
    total_loss = sum(abs(portfolio_impacts.get(s, detail.sp500_decline)) * w 
                     for s, w in zip(portfolio_symbols, portfolio_weights))
    
    st.markdown(f"""
    <div style="background: {detail.color}22; border: 2px solid {detail.color}; border-radius: 12px; 
                padding: 1rem; margin-top: 1rem; text-align: center;">
        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">
            Estimated Total Portfolio Loss
        </div>
        <div style="font-size: 2rem; font-weight: bold; color: {detail.color};">
            -{total_loss*100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 6. SECTOR IMPACTS (if available)
    if detail.sector_impacts:
        st.markdown('<div class="section-title">📊 Sector Performance</div>', unsafe_allow_html=True)
        
        # Sort sectors by impact
        sectors = sorted(detail.sector_impacts.items(), key=lambda x: x[1])
        
        # Create bar chart
        sector_names = [s[0] for s in sectors]
        sector_values = [abs(s[1] * 100) for s in sectors]
        
        fig_sectors = go.Figure()
        
        colors = ['#ef4444' if v > 40 else '#f97316' if v > 25 else '#fbbf24' 
                  for v in sector_values]
        
        fig_sectors.add_trace(go.Bar(
            y=sector_names,
            x=sector_values,
            orientation='h',
            marker=dict(color=colors),
            text=[f'-{v:.1f}%' for v in sector_values],
            textposition='outside'
        ))
        
        fig_sectors.update_layout(
            title="Losses by Sector",
            xaxis_title="Decline (%)",
            height=max(300, len(sectors) * 40),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        fig_sectors.update_xaxes(showgrid=True, gridcolor='#f3f4f6')
        fig_sectors.update_yaxes(showgrid=False)
        
        st.plotly_chart(fig_sectors, use_container_width=True)
    
    # 7. LESSONS LEARNED
    st.markdown('<div class="section-title">🎓 Lessons Learned</div>', unsafe_allow_html=True)
    
    for lesson in detail.lessons_learned:
        st.markdown(f"""
        <div class="lesson-item">
            💡 {lesson}
        </div>
        """, unsafe_allow_html=True)
    
    # Close modal container
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Close button
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("✕ Close", use_container_width=True, type="secondary"):
        st.session_state.pop('selected_scenario', None)
        st.rerun()


def activate_scenario_modal(scenario_name: str):
    """Activate the scenario modal by storing scenario name in session state"""
    st.session_state['selected_scenario'] = scenario_name


def is_scenario_modal_active() -> bool:
    """Check if a scenario modal is currently active"""
    return 'selected_scenario' in st.session_state and st.session_state['selected_scenario'] is not None


def get_active_scenario() -> str:
    """Get the currently active scenario name"""
    return st.session_state.get('selected_scenario', None)