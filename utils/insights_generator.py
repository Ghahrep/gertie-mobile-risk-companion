# utils/insights_generator.py
"""
Generate portfolio insights from risk analysis data
"""

from typing import List, Dict, Optional
import streamlit as st

@st.cache_data(ttl=300, show_spinner=False)
def generate_insights(symbols: tuple, weights: tuple, risk_data: dict) -> List[Dict]:
    """
    Generate actionable insights from portfolio risk data
    
    Args:
        symbols: Tuple of portfolio symbols (for caching)
        weights: Tuple of portfolio weights (for caching)
        risk_data: Risk analysis response from API
    
    Returns:
        List of insight dictionaries with title, description, emoji, and actions
    """
    insights = []
    
    # Handle error case
    if not risk_data or 'error' in risk_data:
        return [{
            'emoji': '⚠️',
            'title': 'Unable to Generate Insights',
            'description': 'Could not fetch portfolio data. Try refreshing.',
            'priority': 'high'
        }]
    
    # Extract metrics
    metrics = risk_data.get('metrics', {})
    
    if not metrics:
        return [{
            'emoji': '📊',
            'title': 'Analyzing Portfolio',
            'description': 'Portfolio analysis in progress. Check back soon.',
            'priority': 'low'
        }]
    
    volatility = metrics.get('annualized_volatility', 0)
    sharpe = metrics.get('sharpe_ratio', 0)
    var_95 = metrics.get('var_95', 0)
    cvar_95 = metrics.get('cvar_95', 0)
    max_drawdown = metrics.get('max_drawdown', 0)
    
    # Insight 1: Volatility Assessment
    if volatility > 0.30:  # High volatility (>30%)
        insights.append({
            'emoji': '⚠️',
            'title': 'High Volatility Detected',
            'description': f'Your portfolio has {volatility*100:.1f}% annual volatility. Consider adding defensive assets like bonds or low-volatility stocks.',
            'priority': 'high',
            'metric': 'volatility',
            'value': volatility
        })
    elif volatility > 0.20:  # Moderate volatility
        insights.append({
            'emoji': '📊',
            'title': 'Moderate Risk Profile',
            'description': f'Portfolio volatility is {volatility*100:.1f}%. This is typical for growth-focused portfolios.',
            'priority': 'medium',
            'metric': 'volatility',
            'value': volatility
        })
    else:  # Low volatility
        insights.append({
            'emoji': '✅',
            'title': 'Stable Portfolio',
            'description': f'Low volatility of {volatility*100:.1f}% suggests good stability. You might have room for higher-return opportunities.',
            'priority': 'low',
            'metric': 'volatility',
            'value': volatility
        })
    
    # Insight 2: Risk-Adjusted Returns (Sharpe Ratio)
    if sharpe < 0.5:
        insights.append({
            'emoji': '📉',
            'title': 'Poor Risk-Adjusted Returns',
            'description': f'Sharpe ratio of {sharpe:.2f} indicates you may not be compensated well for the risk taken. Consider optimization.',
            'priority': 'high',
            'metric': 'sharpe',
            'value': sharpe
        })
    elif sharpe < 1.0:
        insights.append({
            'emoji': '📈',
            'title': 'Average Risk-Adjusted Returns',
            'description': f'Sharpe ratio of {sharpe:.2f}. There may be room for improvement through rebalancing or optimization.',
            'priority': 'medium',
            'metric': 'sharpe',
            'value': sharpe
        })
    else:
        insights.append({
            'emoji': '🎯',
            'title': 'Strong Risk-Adjusted Returns',
            'description': f'Excellent Sharpe ratio of {sharpe:.2f}! Your portfolio is well-balanced for its risk level.',
            'priority': 'low',
            'metric': 'sharpe',
            'value': sharpe
        })
    
    # Insight 3: Tail Risk (CVaR)
    if abs(cvar_95) > 0.05:  # >5% tail risk
        insights.append({
            'emoji': '🔴',
            'title': 'Significant Tail Risk',
            'description': f'In worst scenarios (5% of cases), you could lose {abs(cvar_95)*100:.1f}%. Consider hedging strategies.',
            'priority': 'high',
            'metric': 'cvar',
            'value': cvar_95
        })
    elif abs(cvar_95) > 0.03:  # 3-5% tail risk
        insights.append({
            'emoji': '⚠️',
            'title': 'Moderate Tail Risk',
            'description': f'Potential worst-case loss: {abs(cvar_95)*100:.1f}%. Monitor market conditions closely.',
            'priority': 'medium',
            'metric': 'cvar',
            'value': cvar_95
        })
    else:
        insights.append({
            'emoji': '🛡️',
            'title': 'Low Tail Risk',
            'description': f'Worst-case loss is only {abs(cvar_95)*100:.1f}%. Your portfolio is well-protected.',
            'priority': 'low',
            'metric': 'cvar',
            'value': cvar_95
        })
    
    # Insight 4: Drawdown Risk
    if abs(max_drawdown) > 0.25:  # >25% max drawdown
        insights.append({
            'emoji': '📉',
            'title': 'Large Historical Drawdown',
            'description': f'Your portfolio experienced a {abs(max_drawdown)*100:.1f}% drawdown in the past. Consider diversification.',
            'priority': 'high',
            'metric': 'drawdown',
            'value': max_drawdown
        })
    elif abs(max_drawdown) > 0.15:
        insights.append({
            'emoji': '📊',
            'title': 'Moderate Drawdown History',
            'description': f'Historical drawdown of {abs(max_drawdown)*100:.1f}% is typical for equity portfolios.',
            'priority': 'medium',
            'metric': 'drawdown',
            'value': max_drawdown
        })
    
    # Insight 5: Concentration Risk
    symbols_list = list(symbols)
    if len(symbols_list) < 5:
        insights.append({
            'emoji': '⚠️',
            'title': 'Concentrated Portfolio',
            'description': f'Only {len(symbols_list)} holdings. Consider adding 5-10 more for better diversification.',
            'priority': 'medium',
            'metric': 'concentration',
            'value': len(symbols_list)
        })
    elif len(symbols_list) > 20:
        insights.append({
            'emoji': '📊',
            'title': 'Highly Diversified',
            'description': f'{len(symbols_list)} holdings may be too many to manage effectively. Consider consolidation.',
            'priority': 'low',
            'metric': 'concentration',
            'value': len(symbols_list)
        })
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    insights.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
    
    return insights[:5]  # Return top 5 insights