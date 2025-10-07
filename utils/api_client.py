# utils/api_client.py
"""
API Client for Mobile Risk Co-pilot
Thin wrapper around your existing FastAPI backend
"""

import requests
import os
from typing import Dict, List, Optional
import logging

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
    
    def get_portfolio_health(self, symbols: List[str], weights: Optional[List[float]] = None) -> dict:
        """Get overall portfolio health score"""
        if not symbols:
            return {"score": 0, "status": "No portfolio data"}
        
        # Get risk analysis
        risk_data = self._post("/analyze", {
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
    
    def get_risk_analysis(self, symbols: List[str], weights: Optional[List[float]] = None, period: str = "1year") -> dict:
        """Get comprehensive risk analysis"""
        return self._post("/analyze", {
            "symbols": symbols,
            "weights": weights,
            "period": period,
            "use_real_data": True
        })
    
    def get_risk_attribution(self, symbols: List[str], weights: Optional[List[float]] = None, period: str = "1year") -> dict:
        """Get risk attribution (systematic vs idiosyncratic)"""
        return self._post("/risk-attribution", {
            "symbols": symbols,
            "weights": weights,
            "period": period
        })
    
    def optimize_portfolio(self, symbols: List[str], method: str = "max_sharpe", period: str = "1year") -> dict:
        """Run portfolio optimization"""
        return self._post("/optimize", {
            "symbols": symbols,
            "method": method,
            "period": period
        })
    
    def get_correlation_analysis(self, symbols: List[str], period: str = "1year") -> dict:
        """Get correlation matrix and clustering"""
        return self._post("/correlations", {
            "symbols": symbols,
            "period": period,
            "use_real_data": True
        })
    
    def run_stress_test(self, symbols: List[str], weights: Optional[List[float]] = None, scenarios: Optional[dict] = None) -> dict:
        """Run stress test scenario"""
        return self._post("/stress-test", {
            "symbols": symbols,
            "weights": weights,
            "stress_scenarios": scenarios,
            "period": "1year",
            "use_real_data": True
        })
    
    def get_behavioral_analysis(self, symbols: List[str], conversation_history: List[dict] = None) -> dict:
        """Get behavioral bias analysis"""
        return self._post("/analyze-biases", {
            "symbols": symbols,
            "conversation_history": conversation_history or []
        })
    
    # ==================== HEDGING METHODS ====================
    
    def analyze_hedge_opportunities(
        self, 
        symbols: List[str], 
        weights: Optional[List[float]] = None,
        period: str = "1year",
        top_n: int = 5,
        hedge_candidates: Optional[List[str]] = None,
        timeout: int = 60
    ) -> dict:
        """
        Analyze portfolio and find top hedging opportunities
        
        Note: This is a long-running operation that typically takes 30-40 seconds
        as it evaluates multiple hedge candidates and calculates impact metrics.
        
        Args:
            symbols: Portfolio symbols
            weights: Portfolio weights (optional, will use equal weight if None)
            period: Analysis period
            top_n: Number of top hedges to return
            hedge_candidates: Specific hedge symbols to evaluate (optional)
            timeout: Request timeout in seconds (default 60s for long analysis)
        
        Returns:
            dict with current portfolio metrics and top hedge recommendations
        """
        if weights is None:
            weights = [1.0 / len(symbols)] * len(symbols)
        
        return self._post("/hedging/analyze-opportunities", {
            "symbols": symbols,
            "weights": weights,
            "period": period,
            "top_n": top_n,
            "hedge_candidates": hedge_candidates
        }, timeout=timeout)
    
    def evaluate_hedge(
        self,
        current_symbols: List[str],
        current_weights: List[float],
        hedge_symbol: str,
        hedge_weight: float = 0.10,
        period: str = "1year",
        timeout: int = 30
    ) -> dict:
        """
        Evaluate impact of adding a specific hedge to portfolio
        
        Args:
            current_symbols: Current portfolio symbols
            current_weights: Current portfolio weights
            hedge_symbol: Symbol to evaluate as hedge
            hedge_weight: Allocation to hedge (default 10%)
            period: Analysis period
            timeout: Request timeout in seconds
        
        Returns:
            dict with before/after metrics and improvements
        """
        return self._post("/hedging/evaluate-hedge", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_symbol": hedge_symbol,
            "hedge_weight": hedge_weight,
            "period": period
        }, timeout=timeout)
    
    def compare_hedges(
        self,
        current_symbols: List[str],
        current_weights: List[float],
        hedge_candidates: List[str],
        hedge_weight: float = 0.10,
        period: str = "1year",
        timeout: int = 60
    ) -> dict:
        """
        Compare multiple hedge candidates side-by-side
        
        Note: Long-running operation when comparing many candidates
        
        Args:
            current_symbols: Current portfolio symbols
            current_weights: Current portfolio weights
            hedge_candidates: List of symbols to compare as hedges
            hedge_weight: Allocation to test for each hedge
            period: Analysis period
            timeout: Request timeout in seconds (default 60s)
        
        Returns:
            dict with comparison of all hedge candidates
        """
        return self._post("/hedging/compare-hedges", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_candidates": hedge_candidates,
            "hedge_weight": hedge_weight,
            "period": period
        }, timeout=timeout)
    
    def find_optimal_hedge_allocation(
        self,
        current_symbols: List[str],
        current_weights: List[float],
        hedge_symbol: str,
        objective: str = "min_cvar",
        period: str = "1year",
        timeout: int = 45
    ) -> dict:
        """
        Find optimal allocation to a hedge asset
        
        Args:
            current_symbols: Current portfolio symbols
            current_weights: Current portfolio weights
            hedge_symbol: Hedge symbol to optimize
            objective: Optimization objective ('min_cvar', 'min_volatility', 'max_sharpe')
            period: Analysis period
            timeout: Request timeout in seconds (default 45s for optimization)
        
        Returns:
            dict with optimal allocation and metrics
        """
        return self._post("/hedging/optimal-allocation", {
            "current_symbols": current_symbols,
            "current_weights": current_weights,
            "hedge_symbol": hedge_symbol,
            "objective": objective,
            "period": period
        }, timeout=timeout)
    
    def get_hedge_candidates(self, timeout: int = 10) -> dict:
        """
        Get default hedge candidate universe
        
        Args:
            timeout: Request timeout in seconds
        
        Returns:
            dict with hedge categories and symbols
        """
        try:
            url = f"{self.base_url}/hedging/default-candidates"
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

# Convenience functions
def get_portfolio_health(symbols: List[str] = None, weights: List[float] = None) -> dict:
    """Get portfolio health score"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    return get_api_client().get_portfolio_health(symbols, weights)

def get_risk_analysis(symbols: List[str] = None, weights: List[float] = None) -> dict:
    """Get risk analysis"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    return get_api_client().get_risk_analysis(symbols, weights)

def get_correlation_analysis(symbols: List[str] = None, period: str = "1year") -> dict:
    """Get correlation analysis"""
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    return get_api_client().get_correlation_analysis(symbols, period)