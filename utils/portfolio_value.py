# utils/portfolio_value.py
"""
Calculate real portfolio values based on current prices
"""

import streamlit as st
import requests
from typing import Dict, List, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

# FMP API configuration - Read from Streamlit secrets or environment
def get_fmp_api_key():
    """Get FMP API key from Streamlit secrets or environment"""
    try:
        # Try Streamlit secrets first (for deployed app)
        return st.secrets.get("FMP_API_KEY", "")
    except:
        # Fall back to environment variable (for local development)
        return os.getenv("FMP_API_KEY", "")

FMP_API_KEY = get_fmp_api_key()
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

@st.cache_data(ttl=60, show_spinner=False)  # Cache prices for 1 minute
def get_current_prices(symbols_tuple: Tuple[str, ...]) -> Dict[str, float]:
    """
    Fetch current prices for a list of symbols
    
    Args:
        symbols_tuple: Tuple of stock symbols (tuple for caching)
    
    Returns:
        Dictionary mapping symbol to current price
    """
    symbols = list(symbols_tuple)
    api_key = get_fmp_api_key()  # Get fresh key each time
    
    if not api_key:
        logger.warning("FMP_API_KEY not set, using mock prices")
        # Return mock prices for testing
        return {symbol: 100.0 + (hash(symbol) % 500) for symbol in symbols}
    
    try:
        # Batch fetch current prices from FMP
        symbols_str = ",".join(symbols)
        url = f"{FMP_BASE_URL}/quote/{symbols_str}"
        params = {"apikey": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract prices
        prices = {}
        for item in data:
            symbol = item.get('symbol')
            price = item.get('price', 0)
            if symbol and price:
                prices[symbol] = float(price)
        
        # Fill in missing prices with fallback
        for symbol in symbols:
            if symbol not in prices:
                logger.warning(f"Price not found for {symbol}, using fallback")
                prices[symbol] = 100.0
        
        return prices
        
    except Exception as e:
        logger.error(f"Failed to fetch prices: {e}")
        # Return fallback prices
        return {symbol: 100.0 for symbol in symbols}

def calculate_portfolio_value(
    symbols: List[str],
    weights: List[float],
    total_investment: float = 100000.0
) -> Dict:
    """
    Calculate real portfolio value and holdings
    
    Args:
        symbols: List of stock symbols
        weights: List of portfolio weights (should sum to 1.0)
        total_investment: Total amount invested (default $100,000)
    
    Returns:
        Dictionary with portfolio value details
    """
    if not symbols or not weights:
        return {
            "total_value": 0.0,
            "holdings": [],
            "error": "No portfolio data"
        }
    
    # Get current prices
    prices = get_current_prices(tuple(symbols))
    
    # Calculate holdings
    holdings = []
    total_value = 0.0
    
    for symbol, weight in zip(symbols, weights):
        allocation = total_investment * weight
        price = prices.get(symbol, 0)
        
        if price > 0:
            shares = allocation / price
            current_value = shares * price
        else:
            shares = 0
            current_value = 0
        
        holdings.append({
            "symbol": symbol,
            "weight": weight,
            "allocation": allocation,
            "price": price,
            "shares": shares,
            "current_value": current_value
        })
        
        total_value += current_value
    
    return {
        "total_value": total_value,
        "total_investment": total_investment,
        "holdings": holdings,
        "gain_loss": total_value - total_investment,
        "gain_loss_pct": ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0,
        "prices": prices
    }

def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency"""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.{decimals}f}K"
    else:
        return f"${value:,.{decimals}f}"

def format_percent(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:+.{decimals}f}%"

def get_portfolio_stats(symbols: List[str], weights: List[float]) -> Dict:
    """
    Get portfolio statistics including value
    
    Args:
        symbols: List of stock symbols
        weights: List of portfolio weights
    
    Returns:
        Dictionary with portfolio stats
    """
    # Get portfolio value from session state or use default
    total_investment = st.session_state.get('portfolio_investment', 100000.0)
    
    portfolio_data = calculate_portfolio_value(symbols, weights, total_investment)
    
    return {
        "total_value": portfolio_data["total_value"],
        "total_value_formatted": format_currency(portfolio_data["total_value"]),
        "gain_loss": portfolio_data["gain_loss"],
        "gain_loss_formatted": format_currency(portfolio_data["gain_loss"]),
        "gain_loss_pct": portfolio_data["gain_loss_pct"],
        "gain_loss_pct_formatted": format_percent(portfolio_data["gain_loss_pct"]),
        "holdings_count": len(symbols),
        "holdings": portfolio_data["holdings"]
    }

def initialize_portfolio_investment(default_amount: float = 100000.0):
    """Initialize portfolio investment amount in session state"""
    if 'portfolio_investment' not in st.session_state:
        st.session_state.portfolio_investment = default_amount

def update_portfolio_investment(amount: float):
    """Update portfolio investment amount"""
    st.session_state.portfolio_investment = amount

def get_price_change_24h(symbol: str) -> Optional[float]:
    """
    Get 24-hour price change for a symbol
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Percentage change or None if unavailable
    """
    api_key = get_fmp_api_key()
    
    if not api_key:
        return None
    
    try:
        url = f"{FMP_BASE_URL}/quote/{symbol}"
        params = {"apikey": api_key}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return data[0].get('changesPercentage', 0)
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to fetch 24h change for {symbol}: {e}")
        return None