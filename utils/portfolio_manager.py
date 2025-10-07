# utils/portfolio_manager.py
"""
Portfolio state management for Streamlit session
"""

import streamlit as st
from typing import List, Tuple, Optional

def initialize_portfolio():
    """Initialize portfolio in session state with default values"""
    if 'portfolio_symbols' not in st.session_state:
        # Default portfolio
        st.session_state.portfolio_symbols = ["AAPL", "MSFT", "GOOGL", "NVDA"]
        st.session_state.portfolio_weights = [0.25, 0.25, 0.25, 0.25]

def get_portfolio() -> Tuple[List[str], List[float]]:
    """
    Get current portfolio from session state
    
    Returns:
        Tuple of (symbols, weights)
    """
    initialize_portfolio()  # Ensure initialized
    
    symbols = st.session_state.get('portfolio_symbols', [])
    weights = st.session_state.get('portfolio_weights', [])
    
    return symbols, weights

def set_portfolio(symbols: List[str], weights: Optional[List[float]] = None):
    """
    Set portfolio in session state
    
    Args:
        symbols: List of stock symbols
        weights: List of weights (optional, will use equal weight if None)
    """
    if not symbols:
        return
    
    # If no weights provided, use equal weight
    if weights is None or len(weights) != len(symbols):
        weights = [1.0 / len(symbols)] * len(symbols)
    
    # Normalize weights to sum to 1.0
    total = sum(weights)
    if total > 0:
        weights = [w / total for w in weights]
    
    st.session_state.portfolio_symbols = symbols
    st.session_state.portfolio_weights = weights

def add_to_portfolio(symbol: str, weight: float = 0.1):
    """
    Add a new symbol to portfolio
    
    Args:
        symbol: Stock symbol to add
        weight: Allocation for new symbol (default 10%)
    """
    symbols, weights = get_portfolio()
    
    # Check if already in portfolio
    if symbol in symbols:
        return
    
    # Reduce existing weights proportionally
    reduction_factor = 1.0 - weight
    new_weights = [w * reduction_factor for w in weights]
    
    # Add new symbol
    symbols.append(symbol)
    new_weights.append(weight)
    
    set_portfolio(symbols, new_weights)

def remove_from_portfolio(symbol: str):
    """
    Remove a symbol from portfolio
    
    Args:
        symbol: Stock symbol to remove
    """
    symbols, weights = get_portfolio()
    
    if symbol not in symbols:
        return
    
    # Find and remove
    idx = symbols.index(symbol)
    symbols.pop(idx)
    removed_weight = weights.pop(idx)
    
    # Redistribute weight proportionally
    if symbols and sum(weights) > 0:
        remaining_total = sum(weights)
        weights = [(w / remaining_total) * (1.0 + removed_weight / remaining_total) for w in weights]
    
    set_portfolio(symbols, weights)

def update_weight(symbol: str, new_weight: float):
    """
    Update weight for a specific symbol
    
    Args:
        symbol: Stock symbol
        new_weight: New weight (will be normalized)
    """
    symbols, weights = get_portfolio()
    
    if symbol not in symbols:
        return
    
    idx = symbols.index(symbol)
    weights[idx] = new_weight
    
    # Normalize all weights
    set_portfolio(symbols, weights)

def clear_portfolio():
    """Clear the entire portfolio"""
    st.session_state.portfolio_symbols = []
    st.session_state.portfolio_weights = []

def get_portfolio_size() -> int:
    """Get number of holdings in portfolio"""
    symbols, _ = get_portfolio()
    return len(symbols)