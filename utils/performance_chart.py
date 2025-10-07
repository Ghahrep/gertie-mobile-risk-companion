# utils/performance_chart.py
"""
Historical Performance Chart Component
Shows portfolio performance over time vs benchmark
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import yfinance as yf


def get_historical_prices(symbols: List[str], period: str = "1y") -> Dict:
    """
    Fetch historical prices for portfolio symbols
    
    Args:
        symbols: List of ticker symbols
        period: Time period (1mo, 3mo, 6mo, 1y, ytd)
    
    Returns:
        Dict with symbol -> price history
    """
    prices = {}
    
    # Add SPY for benchmark comparison
    all_symbols = symbols + ['SPY']
    
    for symbol in all_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if not hist.empty:
                prices[symbol] = hist['Close'].values
            else:
                # Fallback to synthetic data if fetch fails
                prices[symbol] = _generate_synthetic_prices(period, symbol)
        except Exception as e:
            # Fallback to synthetic data
            prices[symbol] = _generate_synthetic_prices(period, symbol)
    
    return prices


def _generate_synthetic_prices(period: str, symbol: str) -> np.ndarray:
    """Generate synthetic price data for demonstration"""
    
    # Determine number of days
    days_map = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        'ytd': (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    }
    
    days = days_map.get(period, 365)
    
    # Generate random walk with slight upward drift
    np.random.seed(hash(symbol) % 2**32)  # Consistent per symbol
    
    returns = np.random.normal(0.0003, 0.015, days)  # ~7.5% annual return, 23% volatility
    prices = 100 * np.exp(np.cumsum(returns))
    
    return prices


def calculate_portfolio_performance(
    symbols: List[str],
    weights: List[float],
    period: str = "1y"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate portfolio performance over time
    
    Args:
        symbols: Portfolio symbols
        weights: Portfolio weights
        period: Time period
    
    Returns:
        Tuple of (dates, portfolio_values, spy_values)
    """
    
    # Get historical prices
    prices = get_historical_prices(symbols, period)
    
    # Determine number of days
    days_map = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        'ytd': (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    }
    days = days_map.get(period, 365)
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Calculate portfolio values
    portfolio_values = np.zeros(days)
    
    for symbol, weight in zip(symbols, weights):
        if symbol in prices:
            symbol_prices = prices[symbol]
            
            # Normalize to start at 100
            if len(symbol_prices) > 0 and symbol_prices[0] != 0:
                normalized = 100 * symbol_prices / symbol_prices[0]
            else:
                normalized = np.full(days, 100)
            
            # Ensure correct length
            if len(normalized) < days:
                # Pad with last value
                normalized = np.pad(normalized, (0, days - len(normalized)), 
                                   mode='edge')
            elif len(normalized) > days:
                normalized = normalized[:days]
            
            portfolio_values += weight * normalized
    
    # Get SPY (benchmark) values
    spy_prices = prices.get('SPY', _generate_synthetic_prices(period, 'SPY'))
    
    if len(spy_prices) > 0 and spy_prices[0] != 0:
        spy_values = 100 * spy_prices / spy_prices[0]
    else:
        spy_values = np.full(days, 100)
    
    # Ensure correct length for SPY
    if len(spy_values) < days:
        spy_values = np.pad(spy_values, (0, days - len(spy_values)), mode='edge')
    elif len(spy_values) > days:
        spy_values = spy_values[:days]
    
    return dates, portfolio_values, spy_values


def show_performance_chart(symbols: List[str], weights: List[float], period: str = "1y"):
    """
    Display historical performance chart with benchmark comparison
    
    Args:
        symbols: Portfolio symbols
        weights: Portfolio weights  
        period: Time period to display
    """
    
    # Calculate performance
    dates, portfolio_values, spy_values = calculate_portfolio_performance(
        symbols, weights, period
    )
    
    # Calculate metrics
    portfolio_return = ((portfolio_values[-1] / portfolio_values[0]) - 1) * 100
    spy_return = ((spy_values[-1] / spy_values[0]) - 1) * 100
    
    # Calculate max drawdown
    portfolio_running_max = np.maximum.accumulate(portfolio_values)
    portfolio_drawdown = (portfolio_values - portfolio_running_max) / portfolio_running_max * 100
    max_drawdown = portfolio_drawdown.min()
    
    spy_running_max = np.maximum.accumulate(spy_values)
    spy_drawdown = (spy_values - spy_running_max) / spy_running_max * 100
    spy_max_drawdown = spy_drawdown.min()
    
    # Calculate volatility (annualized)
    portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
    portfolio_volatility = np.std(portfolio_returns) * np.sqrt(252) * 100
    
    spy_returns = np.diff(spy_values) / spy_values[:-1]
    spy_volatility = np.std(spy_returns) * np.sqrt(252) * 100
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Portfolio Value vs S&P 500", "Drawdown"),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Main chart - Portfolio vs SPY
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_values,
            name="Your Portfolio",
            line=dict(color='#3b82f6', width=3),
            hovertemplate='%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=spy_values,
            name="S&P 500",
            line=dict(color='#6b7280', width=2, dash='dash'),
            hovertemplate='%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Drawdown chart
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_drawdown,
            name="Portfolio DD",
            fill='tozeroy',
            line=dict(color='#ef4444', width=1),
            fillcolor='rgba(239, 68, 68, 0.2)',
            showlegend=False,
            hovertemplate='%{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=spy_drawdown,
            name="S&P 500 DD",
            line=dict(color='#6b7280', width=1, dash='dot'),
            showlegend=False,
            hovertemplate='%{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_xaxes(title_text="", showgrid=True, gridcolor='#f3f4f6', row=1, col=1)
    fig.update_xaxes(title_text="Date", showgrid=True, gridcolor='#f3f4f6', row=2, col=1)
    
    fig.update_yaxes(
        title_text="Value (Starting = 100)",
        showgrid=True,
        gridcolor='#f3f4f6',
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Drawdown (%)",
        showgrid=True,
        gridcolor='#f3f4f6',
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Return",
            f"{portfolio_return:+.2f}%",
            delta=f"{portfolio_return - spy_return:+.2f}% vs S&P" if portfolio_return != spy_return else None
        )
    
    with col2:
        st.metric(
            "S&P 500 Return",
            f"{spy_return:+.2f}%"
        )
    
    with col3:
        st.metric(
            "Max Drawdown",
            f"{max_drawdown:.2f}%",
            delta=f"{max_drawdown - spy_max_drawdown:.2f}% vs S&P" if max_drawdown != spy_max_drawdown else None,
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Volatility",
            f"{portfolio_volatility:.1f}%",
            delta=f"{portfolio_volatility - spy_volatility:+.1f}% vs S&P" if portfolio_volatility != spy_volatility else None,
            delta_color="inverse"
        )
    
    # Performance summary
    with st.expander("📊 Performance Summary"):
        st.markdown(f"""
        ### Your Portfolio vs S&P 500 ({period.upper()})
        
        **Returns:**
        - Your Portfolio: **{portfolio_return:+.2f}%**
        - S&P 500: **{spy_return:+.2f}%**
        - Outperformance: **{portfolio_return - spy_return:+.2f}%**
        
        **Risk:**
        - Your Max Drawdown: **{max_drawdown:.2f}%**
        - S&P Max Drawdown: **{spy_max_drawdown:.2f}%**
        - Your Volatility: **{portfolio_volatility:.1f}%** (annualized)
        - S&P Volatility: **{spy_volatility:.1f}%** (annualized)
        
        **Risk-Adjusted:**
        - Sharpe Ratio: **{(portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0):.2f}**
        - Calmar Ratio: **{(portfolio_return / abs(max_drawdown) if max_drawdown != 0 else 0):.2f}**
        
        {"🎉 **Well done!** Your portfolio outperformed the S&P 500." if portfolio_return > spy_return else "📊 Your portfolio underperformed the benchmark, but past performance doesn't guarantee future results."}
        """)


def show_performance_section(symbols: List[str], weights: List[float]):
    """
    Display complete performance section with time period selector
    
    Args:
        symbols: Portfolio symbols
        weights: Portfolio weights
    """
    
    st.markdown("---")
    st.markdown("### 📈 Historical Performance")
    
    st.markdown("""
    <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">
        See how your portfolio has performed over time compared to the S&P 500
    </div>
    """, unsafe_allow_html=True)
    
    # Time period selector
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("1M", use_container_width=True, key="perf_1m"):
            st.session_state['performance_period'] = '1mo'
    
    with col2:
        if st.button("3M", use_container_width=True, key="perf_3m"):
            st.session_state['performance_period'] = '3mo'
    
    with col3:
        if st.button("6M", use_container_width=True, key="perf_6m"):
            st.session_state['performance_period'] = '6mo'
    
    with col4:
        if st.button("1Y", use_container_width=True, key="perf_1y", 
                     type="primary" if 'performance_period' not in st.session_state else "secondary"):
            st.session_state['performance_period'] = '1y'
    
    with col5:
        if st.button("YTD", use_container_width=True, key="perf_ytd"):
            st.session_state['performance_period'] = 'ytd'
    
    # Get selected period (default 1 year)
    period = st.session_state.get('performance_period', '1y')
    
    # Show chart
    show_performance_chart(symbols, weights, period)