# utils/api_client.py
"""
API Client for Mobile Risk Co-pilot
Thin wrapper around your existing FastAPI backend with caching support
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
import logging
import streamlit as st
import hashlib
import json

logger = logging.getLogger(__name__)

# Backend API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "https://risk-analysis-api.onrender.com")

class APIClient:
    """Client for interacting with risk analysis backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.default_timeout = 30
    
    def _post(self, endpoint: str, data: dict, timeout: Optional[int] = None) -> dict:
        """
        Generic POST request with error handling
        
        Args:
            endpoint: API endpoint path
            data: Request payload
            timeout: Request timeout in seconds (uses default_timeout if None)
        
        Returns:
            Response JSON or error dict
        """
        try:
            url = f"{self.base_url}{endpoint}"
            timeout = timeout or self.default_timeout
            logger.info(f"POST {url} (timeout={timeout}s)")
            
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint} after {timeout}s")
            return {"error": f"Request timed out after {timeout} seconds. Please try again."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return {"error": f"Request failed: {str(e)}"}
    
    # ==================== CACHED API CALLS ====================
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_portfolio_health(_self, symbols_tuple: Tuple[str, ...], weights_tuple: Optional[Tuple[float, ...]] = None) -> dict:
        """
        Get overall portfolio health score (cached for 5 minutes)
        
        Note: Uses tuples for hashability in Streamlit cache
        """
        symbols = list(symbols_tuple)
        weights = list(weights_tuple) if weights_tuple else None
        
        if not symbols:
            return {"score": 0, "status": "No portfolio data"}
        
        # Get risk analysis
        risk_data = _self._post("/analyze", {
            "symbols": symbols,
            "weights": weights,
            "period": "1year",
            "use_real_data": True
        })
        
        if "error" in risk_data:
            return {"score": 50, "status": "Unable to calculate"}
        
        # Extract metrics from nested response
        metrics = risk_data.get('metrics', {})
        
        # Calculate health score
        volatility = metrics.get('annualized_volatility', 0.25)
        sharpe = metrics.get('sharpe_ratio', 0)
        
        vol_score = max(0, 100 - (volatility * 200))
        sharpe_score = min(50, sharpe * 25)
        
        score = int(vol_score + sharpe_score)
        
        return {
            "score": score,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "status": "healthy" if score >= 80 else "caution" if score >= 60 else "risk"
        }
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_risk_analysis(_self, symbols_tuple: Tuple[str, ...], weights_tuple: Optional[Tuple[float, ...]] = None, period: str = "1year") -> dict:
        """
        Get comprehensive risk analysis (cached for 5 minutes)
        
        Note: Uses tuples for hashability in Streamlit cache
        """
        symbols = list(symbols_tuple)
        weights = list(weights_tuple) if weights_tuple else None
        
        return _self._post("/analyze", {
            "symbols": symbols,
            "weights": weights,
            "period": period,
            "use_real_data": True
        })
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_risk_attribution(_self, symbols_tuple: Tuple[str, ...], weights_tuple: Optional[Tuple[float, ...]] = None, period: str = "1year") -> dict:
        """Get risk attribution (systematic vs idiosyncratic) - cached"""
        symbols = list(symbols_tuple)
        weights = list(weights_tuple) if weights_tuple else None
        
        return _self._post("/risk-attribution", {
            "symbols": symbols,
            "weights": weights,
            "period": period
        })
    
    @st.cache_data(ttl=600, show_spinner=False)
    def optimize_portfolio(_self, symbols_tuple: Tuple[str, ...], method: str = "max_sharpe", period: str = "1year") -> dict:
        """Run portfolio optimization (cached for 10 minutes)"""
        symbols = list(symbols_tuple)
        
        return _self._post("/optimize", {
            "symbols": symbols,
            "method": method,
            "period": period
        })
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_correlation_analysis(_self, symbols_tuple: Tuple[str, ...], period: str = "1year") -> dict:
        """Get correlation matrix and clustering (cached for 5 minutes)"""
        symbols = list(symbols_tuple)
        
        return _self._post("/correlations", {
            "symbols": symbols,
            "period": period,
            "use_real_data": True
        })
    
    @st.cache_data(ttl=300, show_spinner=False)
    def run_stress_test(_self, symbols_tuple: Tuple[str, ...], weights_tuple: Optional[Tuple[float, ...]] = None, scenarios_json: Optional[str] = None) -> dict:
        """Run stress test scenario (cached for 5 minutes)"""
        symbols = list(symbols_tuple)
        weights = list(weights_tuple) if weights_tuple else None
        scenarios = json.loads(scenarios_json) if scenarios_json else None
        
        return _self._post("/stress-test", {
            "symbols": symbols,
            "weights": weights,
            "stress_scenarios": scenarios,
            "period": "1year",
            "use_real_data": True
        })
    
    def get_behavioral_analysis(self, symbols: List[str], conversation_history: List[dict] = None) -> dict:
        """Get behavioral bias analysis (not cached - conversational)"""
        return self._post("/analyze-biases", {
            "symbols": symbols,
            "conversation_history": conversation_history or []
        })
    
    # ==================== HEDGING METHODS (Long-running, 1-hour cache) ====================
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def analyze_hedge_opportunities(
        _self, 
        symbols_tuple: Tuple[str, ...], 
        weights_tuple: Optional[Tuple[float, ...]] = None,
        period: str = "1year",
        top_n: int = 5,
        hedge_candidates_tuple: Optional[Tuple[str, ...]] = None,
        timeout: int = 60
    ) -> dict:
        """
        Analyze portfolio and find top hedging opportunities (cached for 1 hour)
        
        Note: This is a long-running operation that typically takes 30-40 seconds.
        Results are cached for 1 hour since hedge recommendations don't change frequently.
        """
        symbols = list(symbols_tuple)
        weights = list(weights_tuple) if weights_tuple else None
        hedge_candidates = list(hedge_candidates_tuple) if hedge_candidates_tuple else None
        
        if weights is None:
            weights = [1.0 / len(symbols)] * len(symbols)
        
        return _self._post("/hedging/analyze-opportunities", {
            "symbols": symbols,
            "weights": weights,
            "period": period,
            "top_n": top_n,
            "hedge_candidates": hedge_candidates
        }, timeout=timeout)
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def evaluate_hedge(
        _self,
        current_symbols_tuple: Tuple[str, ...],
        current_weights_tuple: Tuple[float, ...],
        hedge_symbol: str,
        hedge_weight: float = 0.10,
        period: str = "1year",
        timeout: int = 30
    ) -> dict:
        """Evaluate impact of adding a specific hedge (cached for 1 hour)"""
        current_symbols = list(current_symbols_tuple)
        current_weights = list(current_weights_tuple)
        
        return _self._post("/hedging/evaluate-hedge", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_symbol": hedge_symbol,
            "hedge_weight": hedge_weight,
            "period": period
        }, timeout=timeout)
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def compare_hedges(
        _self,
        current_symbols_tuple: Tuple[str, ...],
        current_weights_tuple: Tuple[float, ...],
        hedge_candidates_tuple: Tuple[str, ...],
        hedge_weight: float = 0.10,
        period: str = "1year",
        timeout: int = 60
    ) -> dict:
        """Compare multiple hedge candidates (cached for 1 hour)"""
        current_symbols = list(current_symbols_tuple)
        current_weights = list(current_weights_tuple)
        hedge_candidates = list(hedge_candidates_tuple)
        
        return _self._post("/hedging/compare-hedges", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_candidates": hedge_candidates,
            "hedge_weight": hedge_weight,
            "period": period
        }, timeout=timeout)
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def find_optimal_hedge_allocation(
        _self,
        current_symbols_tuple: Tuple[str, ...],
        current_weights_tuple: Tuple[float, ...],
        hedge_symbol: str,
        objective: str = "min_cvar",
        period: str = "1year",
        timeout: int = 45
    ) -> dict:
        """Find optimal allocation to a hedge asset (cached for 1 hour)"""
        current_symbols = list(current_symbols_tuple)
        current_weights = list(current_weights_tuple)
        
        return _self._post("/hedging/optimal-allocation", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_symbol": hedge_symbol,
            "objective": objective,
            "period": period
        }, timeout=timeout)
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_hedge_candidates(_self, timeout: int = 10) -> dict:
        """Get default hedge candidate universe (cached for 1 hour)"""
        try:
            url = f"{_self.base_url}/hedging/default-candidates"
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get hedge candidates: {e}")
            # Fallback to default candidates
            return {
                "error": str(e),
                "hedge_universe": {
                    "bonds": ["TLT", "BND", "AGG"],
                    "defensive_equity": ["VYM", "USMV"],
                    "alternatives": ["GLD", "VNQ"],
                    "low_volatility": ["SPLV"],
                    "international": ["VEA", "VWO"]
                }
            }

# Singleton instance
_client = None

def get_api_client() -> APIClient:
    """Get or create API client instance"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client

def clear_all_caches():
    """Clear all Streamlit caches - useful for manual refresh"""
    st.cache_data.clear()

# Convenience functions with proper tuple conversion
def get_portfolio_health(symbols: List[str] = None, weights: List[float] = None) -> dict:
    """Get portfolio health score"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    symbols_tuple = tuple(symbols)
    weights_tuple = tuple(weights) if weights else None
    
    return get_api_client().get_portfolio_health(symbols_tuple, weights_tuple)

def get_risk_analysis(symbols: List[str] = None, weights: List[float] = None) -> dict:
    """Get risk analysis"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    symbols_tuple = tuple(symbols)
    weights_tuple = tuple(weights) if weights else None
    
    return get_api_client().get_risk_analysis(symbols_tuple, weights_tuple)

def get_correlation_analysis(symbols: List[str] = None, period: str = "1year") -> dict:
    """Get correlation analysis"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    symbols_tuple = tuple(symbols)
    
    return get_api_client().get_correlation_analysis(symbols_tuple, period)