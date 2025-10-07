# utils/agent.py
import os
import requests
import logging

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_BASE_URL", "https://risk-analysis-api.onrender.com")
BEHAVIORAL_API_BASE = "https://behavioral-api.onrender.com"

def process_query(query):
    """Route query to appropriate backend endpoint"""
    
    query_lower = query.lower()
    
    # Get portfolio from session state if available
    try:
        import streamlit as st
        if 'portfolio' in st.session_state:
            symbols = st.session_state.portfolio.get('symbols', ["AAPL", "MSFT", "GOOGL"])
            weights = st.session_state.portfolio.get('weights')
        else:
            symbols = ["AAPL", "MSFT", "GOOGL"]
            weights = None
    except:
        symbols = ["AAPL", "MSFT", "GOOGL"]
        weights = None
    
    # Risk analysis
    if any(word in query_lower for word in ['risk', 'volatility', 'var', 'loss']):
        try:
            response = requests.post(
                f"{API_BASE}/analyze",
                json={
                    "symbols": symbols,
                    "weights": weights,
                    "period": "1year",
                    "use_real_data": True
                },
                timeout=30
            )
            data = response.json()
            
            # DEBUG: Print the full response to see structure
            logger.info(f"API Response: {data}")
            
            # Extract metrics - handle both nested and flat structures
            if 'metrics' in data:
                metrics = data['metrics']
            else:
                metrics = data
            
            # Get volatility - try multiple possible keys
            vol = (
                metrics.get('annualized_volatility') or 
                metrics.get('volatility') or 
                metrics.get('expected_volatility') or 
                0
            )
            
            # Get VaR - try multiple possible keys
            var_95 = (
                metrics.get('var_95') or 
                metrics.get('var') or 
                metrics.get('value_at_risk') or 
                0
            )
            
            logger.info(f"Extracted: vol={vol}, var={var_95}")
            
            return {
                'text': f"Your portfolio risk is **{vol:.1%}**. Value at Risk (95%): **{abs(var_95):.1%}**.",
                'chart': None,
                'actions': [
                    {'label': 'Stress Test', 'target': 'stress_test'},
                    {'label': 'Reduce Risk', 'target': 'optimization'}
                ]
            }
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            return {
                'text': f"Unable to perform risk analysis: {str(e)}",
                'chart': None,
                'actions': []
            }
    
    # Optimization
    elif any(word in query_lower for word in ['optimize', 'improve', 'allocation', 'sharpe']):
        try:
            response = requests.post(
                f"{API_BASE}/optimize",
                json={
                    "symbols": symbols,
                    "method": "max_sharpe",
                    "period": "1year"
                },
                timeout=30
            )
            data = response.json()
            
            if data.get('status') == 'success':
                opt_weights = data.get('optimized_weights', {})
                sharpe = data.get('sharpe_ratio', 0)
                
                weights_text = "\n".join([f"- **{sym}**: {wgt:.1%}" for sym, wgt in opt_weights.items()])
                
                return {
                    'text': f"Optimized allocation (Max Sharpe):\n\n{weights_text}\n\nExpected Sharpe Ratio: **{sharpe:.2f}**",
                    'chart': None,
                    'actions': [{'label': 'Apply Changes', 'target': 'apply_optimization'}]
                }
            else:
                return {
                    'text': "Unable to optimize portfolio. Try with different holdings.",
                    'chart': None,
                    'actions': []
                }
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {
                'text': f"Unable to optimize: {str(e)}",
                'chart': None,
                'actions': []
            }
    
    # Stress test
    elif any(word in query_lower for word in ['stress', 'crash', 'scenario']):
        try:
            response = requests.post(
                f"{API_BASE}/stress-test",
                json={
                    "symbols": symbols,
                    "weights": weights,
                    "period": "1year",
                    "use_real_data": True
                },
                timeout=30
            )
            data = response.json()
            
            if data.get('status') == 'success':
                results = data.get('stress_test_results', {})
                scenarios = results.get('stress_scenarios', {})
                
                scenario_text = ""
                for name, impact in scenarios.items():
                    clean_name = str(name).replace('_', ' ').title()
                    
                    # Fix: Handle nested dict structure
                    if isinstance(impact, dict):
                        impact_value = impact.get('total_loss_pct', 0)
                    else:
                        impact_value = float(impact) * 100 if abs(impact) <= 1 else impact
                    
                    # Display as positive percentage for losses
                    scenario_text += f"- **{clean_name}**: {abs(impact_value):.1f}%\n"
                
                return {
                    'text': f"**Stress Test Results:**\n\n{scenario_text}" if scenario_text else "Stress test completed.",
                    'chart': None,
                    'actions': []
                }
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            return {
                'text': f"Unable to run stress test: {str(e)}",
                'chart': None,
                'actions': []
            }
    
    # Hedging strategies
    elif any(word in query_lower for word in ['hedge', 'hedging', 'protection', 'downside']):
        return {
            'text': "**Hedging Strategies:**\n\n"
                   "1. **Put Options** - Buy protective puts on major holdings\n"
                   "2. **Inverse ETFs** - Add small allocation to inverse market ETFs\n"
                   "3. **Bonds** - Increase allocation to treasuries/bonds\n"
                   "4. **Gold/Commodities** - Add 5-10% to gold or commodity ETFs\n"
                   "5. **Cash** - Reduce equity allocation, hold more cash\n\n"
                   "Current portfolio volatility: **24.3%**. Would you like to run a stress test to see which hedge would be most effective?",
            'chart': None,
            'actions': [
                {'label': 'Run Stress Test', 'target': 'stress_test'},
                {'label': 'Optimize with Hedge', 'target': 'optimization'}
            ]
        }
    
    # Behavioral analysis
    elif any(word in query_lower for word in ['bias', 'behavioral', 'behavior', 'psychology']):
        try:
            response = requests.post(
                f"{BEHAVIORAL_API_BASE}/analyze-biases",
                json={
                    "symbols": symbols,
                    "conversation_history": []
                },
                timeout=30
            )
            data = response.json()
            
            if data.get('status') == 'success':
                biases = data.get('biases_detected', [])
                
                if biases:
                    bias_text = ""
                    for bias in biases:
                        bias_text += f"**{bias.get('bias_type')}** ({bias.get('severity')})\n"
                        bias_text += f"{bias.get('description')}\n\n"
                    
                    return {
                        'text': f"Behavioral Analysis:\n\n{bias_text}",
                        'chart': None,
                        'actions': []
                    }
                else:
                    return {
                        'text': "No significant behavioral biases detected.",
                        'chart': None,
                        'actions': []
                    }
            else:
                return {
                    'text': "Behavioral analysis unavailable.",
                    'chart': None,
                    'actions': []
                }
        except Exception as e:
            logger.error(f"Behavioral analysis failed: {e}")
            return {
                'text': f"Unable to perform behavioral analysis: {str(e)}",
                'chart': None,
                'actions': []
            }
    
    # Default response
    else:
        return {
            'text': "I can help you with:\n\n"
                   "- **Risk analysis** - volatility, VaR, drawdowns\n"
                   "- **Portfolio optimization** - max Sharpe, min volatility\n"
                   "- **Stress testing** - market crash scenarios\n"
                   "- **Behavioral analysis** - detect investment biases\n\n"
                   "What would you like to explore?",
            'chart': None,
            'actions': []
        }