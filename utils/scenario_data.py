# utils/scenario_data.py
"""
Historical Scenario Data Library
Comprehensive information about market crashes and stress scenarios
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ScenarioDetail:
    """Detailed information about a historical scenario"""
    name: str
    icon: str
    color: str
    date_range: str
    description: str
    what_happened: List[str]
    impact_summary: str
    sp500_decline: float
    duration_months: int
    recovery_months: int
    peak_recovery_date: str
    sector_impacts: Dict[str, float]  # Sector name -> % decline
    lessons_learned: List[str]

# =============================================================================
# HISTORICAL SCENARIO DATABASE
# =============================================================================

SCENARIO_DATABASE = {
    "2008 Crisis": ScenarioDetail(
        name="2008 Financial Crisis",
        icon="🔥",
        color="#ef4444",
        date_range="September 2008 - March 2009",
        description="The worst financial crisis since the Great Depression, triggered by the collapse of the U.S. housing market and widespread mortgage defaults.",
        what_happened=[
            "Lehman Brothers collapsed on September 15, 2008",
            "Housing bubble burst after years of subprime lending",
            "Credit markets froze globally",
            "Major banks required government bailouts",
            "Unemployment reached 10% in the U.S.",
            "Global stock markets crashed simultaneously"
        ],
        impact_summary="Markets lost $16.4 trillion in value globally. The S&P 500 fell 57% from peak to trough.",
        sp500_decline=-0.57,
        duration_months=6,
        recovery_months=18,
        peak_recovery_date="March 2013",
        sector_impacts={
            "Financials": -0.65,
            "Technology": -0.45,
            "Consumer Discretionary": -0.52,
            "Industrials": -0.58,
            "Energy": -0.62,
            "Healthcare": -0.35,
            "Utilities": -0.28,
            "Consumer Staples": -0.22
        },
        lessons_learned=[
            "Diversification matters: Bonds and defensive stocks held up better",
            "Leverage amplifies losses during crashes",
            "Financial sector was hardest hit due to direct exposure",
            "Recovery took 4+ years to reach previous peaks",
            "Government intervention prevented complete collapse"
        ]
    ),
    
    "COVID 2020": ScenarioDetail(
        name="COVID-19 Pandemic Crash",
        icon="🌊",
        color="#f97316",
        date_range="February - March 2020",
        description="Fastest bear market in history, triggered by global pandemic lockdowns and economic uncertainty.",
        what_happened=[
            "COVID-19 pandemic declared on March 11, 2020",
            "Global lockdowns shut down economies",
            "Oil prices briefly went negative",
            "S&P 500 fell 34% in just 33 days",
            "Unprecedented monetary and fiscal stimulus",
            "Fastest recovery in stock market history"
        ],
        impact_summary="Despite the severity, markets recovered to new highs within 6 months due to massive stimulus.",
        sp500_decline=-0.34,
        duration_months=1,
        recovery_months=5,
        peak_recovery_date="August 2020",
        sector_impacts={
            "Energy": -0.55,
            "Financials": -0.42,
            "Industrials": -0.38,
            "Consumer Discretionary": -0.35,
            "Technology": -0.22,
            "Healthcare": -0.18,
            "Consumer Staples": -0.15,
            "Utilities": -0.20
        },
        lessons_learned=[
            "Tech stocks proved resilient during pandemic",
            "Speed matters: Fastest crash but fastest recovery",
            "Government stimulus can rapidly reverse declines",
            "Stay-at-home stocks (tech, e-commerce) thrived",
            "Traditional defensive plays (bonds, gold) worked as hedges"
        ]
    ),
    
    "Dot Com": ScenarioDetail(
        name="Dot-Com Bubble Burst",
        icon="💻",
        color="#f59e0b",
        date_range="March 2000 - October 2002",
        description="The collapse of overvalued internet and technology stocks after years of speculation.",
        what_happened=[
            "NASDAQ peaked at 5,048 in March 2000",
            "Tech stocks crashed as profits failed to materialize",
            "9/11 attacks in 2001 accelerated the decline",
            "Accounting scandals (Enron, WorldCom) eroded trust",
            "NASDAQ fell 78% from peak to trough",
            "Many dot-com companies went bankrupt"
        ],
        impact_summary="Technology sector lost $5 trillion in value. It took 15 years for NASDAQ to recover to 2000 peaks.",
        sp500_decline=-0.49,
        duration_months=30,
        recovery_months=60,
        peak_recovery_date="May 2007",
        sector_impacts={
            "Technology": -0.78,
            "Telecommunications": -0.72,
            "Consumer Discretionary": -0.42,
            "Industrials": -0.38,
            "Financials": -0.35,
            "Energy": -0.28,
            "Healthcare": -0.18,
            "Utilities": -0.12
        },
        lessons_learned=[
            "Valuations matter: Unprofitable growth companies crashed hardest",
            "Diversification across sectors is crucial",
            "Recovery from sector-specific crashes takes much longer",
            "Not all tech companies survived (pets.com, WebVan, etc.)",
            "Traditional value stocks outperformed during recovery"
        ]
    ),
    
    "Correction": ScenarioDetail(
        name="Market Correction",
        icon="⚡",
        color="#fbbf24",
        date_range="Typical: 2-4 months",
        description="A standard 10-20% market decline that occurs regularly, roughly every 1-2 years on average.",
        what_happened=[
            "Normal market volatility event",
            "Usually triggered by Fed policy, geopolitical events, or profit-taking",
            "S&P 500 declines 10-20% from recent highs",
            "Lasts 2-4 months on average",
            "Part of healthy market cycles",
            "Recovery typically within 4-6 months"
        ],
        impact_summary="Corrections are normal and healthy. The market has experienced 36 corrections of 10%+ since 1950.",
        sp500_decline=-0.15,
        duration_months=3,
        recovery_months=4,
        peak_recovery_date="Within 6 months",
        sector_impacts={
            "Technology": -0.18,
            "Consumer Discretionary": -0.16,
            "Financials": -0.15,
            "Industrials": -0.14,
            "Energy": -0.14,
            "Healthcare": -0.12,
            "Consumer Staples": -0.08,
            "Utilities": -0.07
        },
        lessons_learned=[
            "Corrections are normal and should be expected",
            "Don't panic-sell during routine corrections",
            "Often good buying opportunities for long-term investors",
            "Defensive sectors decline less during corrections",
            "Usually recover faster than bear markets"
        ]
    ),
    
    "Flash Crash": ScenarioDetail(
        name="Flash Crash",
        icon="💨",
        color="#84cc16",
        date_range="Single Day Event",
        description="Rapid, deep market decline that recovers within hours or days, often driven by algorithmic trading.",
        what_happened=[
            "May 6, 2010: Dow fell 1,000 points in minutes",
            "Triggered by algorithmic trading errors",
            "Market recovered most losses same day",
            "Exposed vulnerabilities in electronic trading",
            "Circuit breakers implemented after",
            "Similar events: Feb 2018, March 2020"
        ],
        impact_summary="Short-lived but severe intraday volatility. Usually recovers within 1-2 days.",
        sp500_decline=-0.09,
        duration_months=0,
        recovery_months=0,
        peak_recovery_date="Same day",
        sector_impacts={
            "All sectors equally affected": -0.09
        },
        lessons_learned=[
            "Intraday volatility can be extreme",
            "Don't panic during flash crashes",
            "Limit orders can be dangerous during volatile periods",
            "Markets have circuit breakers to prevent cascades",
            "Usually technical, not fundamental issues"
        ]
    ),
    
    "Black Monday": ScenarioDetail(
        name="Black Monday 1987",
        icon="📉",
        color="#dc2626",
        date_range="October 19, 1987",
        description="The largest single-day stock market crash in history, with the Dow falling 22.6% in one day.",
        what_happened=[
            "Dow Jones fell 22.6% on October 19, 1987",
            "Triggered by program trading and portfolio insurance",
            "Global markets crashed simultaneously",
            "No clear fundamental cause",
            "Fed cut rates and provided liquidity",
            "Market fully recovered within 2 years"
        ],
        impact_summary="Worst single-day crash ever, but recovery was relatively quick compared to other major crashes.",
        sp500_decline=-0.34,
        duration_months=2,
        recovery_months=20,
        peak_recovery_date="July 1989",
        sector_impacts={
            "Financials": -0.40,
            "Technology": -0.38,
            "Industrials": -0.35,
            "Consumer Discretionary": -0.33,
            "Energy": -0.32,
            "Healthcare": -0.28,
            "Consumer Staples": -0.25,
            "Utilities": -0.22
        },
        lessons_learned=[
            "Markets can crash without clear fundamental reason",
            "Circuit breakers now prevent single-day 20%+ drops",
            "Recovery was faster than feared",
            "Fed intervention matters",
            "Staying invested paid off within 2 years"
        ]
    ),
    
    "Asian Crisis": ScenarioDetail(
        name="Asian Financial Crisis",
        icon="🌏",
        color="#fb923c",
        date_range="July 1997 - December 1998",
        description="Currency and financial crisis that started in Thailand and spread across Asia, affecting global markets.",
        what_happened=[
            "Thai baht collapse triggered regional contagion",
            "Indonesia, South Korea, Malaysia severely affected",
            "Russia defaulted on debt in 1998",
            "Long-Term Capital Management (LTCM) hedge fund collapsed",
            "Fed orchestrated LTCM bailout",
            "Asian currencies lost 30-50% of value"
        ],
        impact_summary="Regional crisis that became global. U.S. markets fell 19% during 1998 volatility.",
        sp500_decline=-0.19,
        duration_months=6,
        recovery_months=12,
        peak_recovery_date="December 1999",
        sector_impacts={
            "Financials": -0.25,
            "Energy": -0.22,
            "Industrials": -0.20,
            "Technology": -0.18,
            "Consumer Discretionary": -0.17,
            "Healthcare": -0.12,
            "Consumer Staples": -0.10,
            "Utilities": -0.08
        },
        lessons_learned=[
            "Emerging market crises can affect developed markets",
            "Currency risk is real for international investments",
            "Contagion effects can spread globally",
            "Domestic U.S. stocks proved more resilient",
            "Fed put in place (central bank intervention)"
        ]
    ),
    
    "Oil Shock": ScenarioDetail(
        name="Oil Price Shock",
        icon="🛢️",
        color="#f87171",
        date_range="1973-1974 & 1979-1980",
        description="Oil supply disruptions caused by Middle East conflicts led to recessions and stagflation.",
        what_happened=[
            "1973: Arab oil embargo quadrupled oil prices",
            "1979: Iranian Revolution disrupted supply",
            "Gas lines and rationing in the U.S.",
            "Inflation + recession = stagflation",
            "Fed raised rates to 20% to combat inflation",
            "S&P 500 fell 48% (1973-1974)"
        ],
        impact_summary="Energy crisis led to the worst inflation in modern history and deep recessions.",
        sp500_decline=-0.48,
        duration_months=18,
        recovery_months=36,
        peak_recovery_date="November 1980",
        sector_impacts={
            "Consumer Discretionary": -0.55,
            "Financials": -0.52,
            "Industrials": -0.50,
            "Technology": -0.48,
            "Healthcare": -0.42,
            "Consumer Staples": -0.35,
            "Energy": +0.20,  # Energy stocks actually went UP
            "Utilities": -0.38
        },
        lessons_learned=[
            "Energy stocks can be a hedge during oil crises",
            "Inflation can persist for years",
            "Commodities (gold) perform well during inflation",
            "High interest rates eventually break inflation",
            "Stagflation is particularly damaging"
        ]
    )
}


def get_scenario_detail(scenario_name: str) -> ScenarioDetail:
    """Get detailed information about a scenario"""
    
    # Normalize the input name
    normalized_name = scenario_name.strip()
    
    # Try exact match first
    if normalized_name in SCENARIO_DATABASE:
        return SCENARIO_DATABASE[normalized_name]
    
    # Try case-insensitive partial matching
    normalized_lower = normalized_name.lower()
    
    for key, detail in SCENARIO_DATABASE.items():
        key_lower = key.lower()
        # Check if key contains the search term or vice versa
        if normalized_lower in key_lower or key_lower in normalized_lower:
            return detail
        
        # Also check just the core terms
        if 'covid' in normalized_lower and 'covid' in key_lower:
            return detail
        if '2008' in normalized_lower and '2008' in key_lower:
            return detail
        if 'dot' in normalized_lower and 'dot' in key_lower:
            return detail
        if 'correction' in normalized_lower and 'correction' in key_lower:
            return detail
        if 'flash' in normalized_lower and 'flash' in key_lower:
            return detail
        if 'black' in normalized_lower and 'black' in key_lower:
            return detail
        if 'asian' in normalized_lower and 'asian' in key_lower:
            return detail
        if 'oil' in normalized_lower and 'oil' in key_lower:
            return detail
    
    # Return default if not found
    return ScenarioDetail(
        name=scenario_name,
        icon="📊",
        color="#6b7280",
        date_range="Unknown",
        description="Historical market stress scenario",
        what_happened=["Market declined significantly"],
        impact_summary="Details not available",
        sp500_decline=-0.20,
        duration_months=3,
        recovery_months=6,
        peak_recovery_date="Unknown",
        sector_impacts={},
        lessons_learned=["Diversification is important", "Stay invested long-term"]
    )


def get_all_scenario_names() -> List[str]:
    """Get list of all available scenario names"""
    return list(SCENARIO_DATABASE.keys())


def estimate_portfolio_impact(
    scenario_name: str,
    portfolio_symbols: List[str],
    portfolio_weights: List[float]
) -> Dict[str, float]:
    """
    Estimate how each asset in portfolio would perform during scenario
    
    Args:
        scenario_name: Name of scenario
        portfolio_symbols: List of ticker symbols
        portfolio_weights: List of weights
    
    Returns:
        Dict mapping symbol -> estimated % decline
    """
    detail = get_scenario_detail(scenario_name)
    
    # Map common tickers to sectors
    TICKER_TO_SECTOR = {
        # Tech
        "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
        "GOOG": "Technology", "NVDA": "Technology", "META": "Technology",
        "TSLA": "Consumer Discretionary", "AMZN": "Consumer Discretionary",
        
        # Finance
        "JPM": "Financials", "BAC": "Financials", "GS": "Financials",
        "MS": "Financials", "WFC": "Financials",
        
        # Healthcare
        "JNJ": "Healthcare", "UNH": "Healthcare", "PFE": "Healthcare",
        "ABBV": "Healthcare", "TMO": "Healthcare",
        
        # Consumer
        "WMT": "Consumer Staples", "PG": "Consumer Staples", 
        "KO": "Consumer Staples", "PEP": "Consumer Staples",
        
        # Energy
        "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
        
        # ETFs
        "SPY": "All sectors equally affected", "QQQ": "Technology",
        "VTI": "All sectors equally affected", "VOO": "All sectors equally affected",
        "TLT": "Bonds (Safe Haven)", "BND": "Bonds (Safe Haven)",
        "GLD": "Gold (Safe Haven)", "SLV": "Commodities"
    }
    
    impacts = {}
    
    for symbol in portfolio_symbols:
        sector = TICKER_TO_SECTOR.get(symbol, "All sectors equally affected")
        
        # Special handling for safe havens
        if "Safe Haven" in sector or "Bonds" in sector:
            # Bonds and gold typically decline less or rise during crashes
            impacts[symbol] = detail.sp500_decline * 0.3  # 30% of S&P decline
        elif sector in detail.sector_impacts:
            impacts[symbol] = detail.sector_impacts[sector]
        else:
            # Use S&P 500 decline as default
            impacts[symbol] = detail.sp500_decline
    
    return impacts