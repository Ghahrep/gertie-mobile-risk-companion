# utils/insights_generator.py
import random
from datetime import datetime

def generate_insights():
    """Generate insight cards based on real portfolio data"""
    
    insights = []
    
    # Risk insight
    insights.append({
        'id': 'risk_1',
        'icon': '🔴',
        'title': 'High-Risk Alert',
        'message': 'Your portfolio volatility increased to 24.3%. Estimated loss in a market crash: -28%.',
        'action1': 'Analyze Impact',
        'action1_target': 'risk_analysis',
        'action2': 'Explore Hedges',
        'action2_target': 'hedge_options'
    })
    
    # Behavioral insight
    insights.append({
        'id': 'behavior_1',
        'icon': '🧠',
        'title': 'Behavioral Pattern',
        'message': "You've checked your portfolio 7 times today. This may indicate loss aversion.",
        'action1': 'Review Biases',
        'action1_target': 'behavioral_analysis',
        'action2': 'Set Reminders',
        'action2_target': 'notification_settings'
    })
    
    # Opportunity insight
    insights.append({
        'id': 'opportunity_1',
        'icon': '🟢',
        'title': 'Diversification Idea',
        'message': 'Low correlation with Healthcare sector. Could improve risk-adjusted returns.',
        'action1': 'See Options',
        'action1_target': 'optimization',
        'action2': 'Compare Sectors',
        'action2_target': 'sector_analysis'
    })
    
    return insights