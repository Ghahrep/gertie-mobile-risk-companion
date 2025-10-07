# utils/tooltips.py
"""
Educational Tooltips Component
Provides inline tooltips and expandable "Learn More" sections for financial metrics
"""

import streamlit as st
from typing import Optional

# =============================================================================
# EDUCATIONAL CONTENT LIBRARY
# =============================================================================

TOOLTIP_CONTENT = {
    "risk_score": {
        "short": "Overall portfolio health (0-100). Higher is better.",
        "long": """
**Risk Score** is a single number (0-100) that summarizes your portfolio's overall health.

**What it means:**
- **80-100 (Green):** Healthy portfolio with good risk-adjusted returns
- **60-79 (Yellow):** Moderate risk, consider optimization
- **0-59 (Red):** High risk, portfolio needs attention

**How it's calculated:**
Combines your volatility and Sharpe ratio to give you a quick health check.

**What to do:**
- Green: You're good! Monitor regularly
- Yellow: Consider rebalancing or adding defensive assets
- Red: Review your holdings and run optimization
""",
        "example": "A score of 75 means your portfolio is reasonably healthy but has room for improvement through better diversification or risk management."
    },
    
    "volatility": {
        "short": "How much your portfolio value swings up and down. Lower is more stable.",
        "long": """
**Volatility** measures how much your portfolio's value bounces around.

**Think of it like:**
A calm lake (low volatility) vs. ocean waves (high volatility)

**What the numbers mean:**
- **5-10%:** Very stable (bonds, conservative funds)
- **15-20%:** Moderate (balanced portfolio)
- **25-35%:** High (growth stocks, tech-heavy)
- **40%+:** Very high (aggressive, concentrated positions)

**Real example:**
If your portfolio has 20% volatility and is worth $100,000:
- On 95% of days, it moves less than $130
- Your typical monthly swing is about ±$5,800
- Annual range is roughly ±$20,000

**Why it matters:**
High volatility = more stress and bigger drawdowns during market crashes.
""",
        "example": "A portfolio with 30% volatility will swing about 3x more than one with 10% volatility."
    },
    
    "var": {
        "short": "Your maximum expected daily loss 95% of the time.",
        "long": """
**VaR (Value at Risk)** tells you: "On 95% of days, I won't lose more than this amount."

**Plain English:**
If your VaR is 2.5%, on a typical bad day (happens once per month), you'll lose about 2.5%.

**What it means for you:**
- **VaR of 1.5%:** Very conservative, rare big losses
- **VaR of 2.5%:** Moderate, expect monthly dips
- **VaR of 4%+:** Aggressive, frequent large swings

**Example:**
- Portfolio value: $100,000
- VaR 95%: 2.5%
- **Meaning:** On 95% of days, losses stay under $2,500. But 5% of days (once per month) could be worse.

**Why 95%?**
We focus on the worst 5% of days because those are when you need to stay calm and not panic-sell.
""",
        "example": "If VaR is 3%, and your portfolio is worth $50,000, you won't lose more than $1,500 on 19 out of 20 trading days."
    },
    
    "cvar": {
        "short": "Average loss on your worst days (worst 5%). Shows tail risk.",
        "long": """
**CVaR (Conditional Value at Risk)** or **Tail Risk** answers: "When things go really wrong, how bad is it on average?"

**The difference from VaR:**
- VaR: Maximum loss 95% of the time
- CVaR: Average loss on the worst 5% of days

**Think of it as:**
Your "disaster insurance" metric. CVaR tells you what to expect during market crashes.

**What the numbers mean:**
- **CVaR of 2%:** Low tail risk (conservative portfolio)
- **CVaR of 3-4%:** Moderate tail risk (balanced)
- **CVaR of 5%+:** High tail risk (aggressive, concentrated)

**Real example:**
- VaR: 2.5% (typical bad day)
- CVaR: 3.8% (disaster day)
- **Meaning:** On regular bad days you lose 2.5%, but on your worst 5% of days, average loss is 3.8%.

**Why it matters:**
High CVaR means market crashes hurt you more. This is where hedging helps most.
""",
        "example": "Portfolio with 4% CVaR: On the worst 1 in 20 days, you lose 4% on average. During COVID 2020 crash, you might have lost 15-20% in a single day."
    },
    
    "sharpe_ratio": {
        "short": "Return per unit of risk. Higher is better (above 1.0 is good).",
        "long": """
**Sharpe Ratio** measures bang-for-buck: How much return do you get for each unit of risk?

**Formula (simplified):**
Sharpe = (Your Returns - Safe Returns) / Your Volatility

**What the numbers mean:**
- **Below 0:** You'd be better off in cash
- **0-0.5:** Poor risk-adjusted returns
- **0.5-1.0:** Acceptable
- **1.0-2.0:** Good (this is the target!)
- **2.0+:** Excellent (rare)

**Real example:**
Portfolio A: 15% return, 20% volatility → Sharpe = 0.65
Portfolio B: 12% return, 10% volatility → Sharpe = 1.00
**Portfolio B is better!** Gets more return per unit of risk.

**Why it matters:**
High returns don't mean much if you take massive risk. Sharpe tells you the "efficiency" of your portfolio.

**What to do:**
If your Sharpe is below 1.0, consider optimization or adding defensive assets.
""",
        "example": "A Sharpe of 1.5 means you earn 1.5% of extra return for every 1% of volatility you accept."
    },
    
    "resilience": {
        "short": "How well your portfolio withstands crashes (0-100). Higher is better.",
        "long": """
**Portfolio Resilience** is a 0-100 score showing how well you survive market crashes.

**How it's calculated:**
Resilience = 100 - Worst Case Loss %

**What it means:**
- **70-100 (Green):** Strong protection, limited crash damage
- **40-69 (Yellow):** Moderate protection, manageable losses
- **0-39 (Red):** Vulnerable, severe losses in crashes

**Real example:**
- Worst case loss: 37%
- Resilience: 100 - 37 = **63**
- **Meaning:** Moderately resilient, would lose over a third in severe crashes

**Comparison:**
- 60/40 Stock/Bond portfolio: Resilience ~75-80
- 100% Tech stocks: Resilience ~40-50
- Conservative bonds: Resilience ~85-95

**Why it matters:**
High resilience = you can sleep at night during crashes. Low resilience = you need hedging.
""",
        "example": "If your resilience is 55, you'd lose about 45% in a 2008-style crisis. Adding bonds or gold could improve this to 70+."
    },
    
    "worst_case": {
        "short": "Expected loss in severe market crash (like 2008 or COVID).",
        "long": """
**Worst Case Scenario** shows how much you'd lose in a severe market crash.

**What we test:**
Historical crises: 2008 Financial Crisis, COVID 2020, Dot-com Bubble, etc.

**What the numbers mean:**
- **10-20% loss:** Well-protected (bonds, defensive)
- **25-35% loss:** Moderate exposure (balanced)
- **40%+ loss:** High vulnerability (concentrated, aggressive)

**Real examples:**
- **2008 Crisis:** S&P 500 fell -37%, tech stocks fell -50%+
- **COVID 2020:** S&P 500 fell -34% in one month
- **Dot-com 2000:** Tech stocks fell -78% over 2 years

**What to do:**
If your worst case is over 40%, consider:
- Adding bonds (TLT, BND)
- Adding gold (GLD)
- Diversifying internationally
- Using defensive stocks (utilities, consumer staples)

**Recovery time:**
Larger losses take longer to recover. A 50% loss needs a 100% gain to break even.
""",
        "example": "A tech-heavy portfolio might show -45% worst case, meaning in a 2008-style crash, $100,000 becomes $55,000."
    },
    
    "correlation": {
        "short": "How much two assets move together (-1 to +1). Lower is better for diversification.",
        "long": """
**Correlation** measures how two assets move together.

**The scale:**
- **+1.0:** Move perfectly together (no diversification benefit)
- **0.0:** Move independently (good diversification)
- **-1.0:** Move in opposite directions (excellent hedge)

**Real examples:**
- Stocks & Stocks: +0.7 to +0.9 (highly correlated)
- Stocks & Bonds: -0.2 to +0.3 (low/negative - good!)
- Stocks & Gold: 0.0 to +0.2 (independent - great!)
- Tech stocks & Tech stocks: +0.85 (very similar)

**Why it matters:**
If everything moves together, you're not diversified. When stocks crash, everything crashes.

**What to aim for:**
Average portfolio correlation below 0.6 is good. Below 0.4 is excellent.

**Example:**
Your tech portfolio (AAPL, GOOGL, MSFT, NVDA) likely has 0.8+ correlation.
Adding TLT (correlation: -0.2) reduces this significantly.
""",
        "example": "If stocks and bonds have -0.3 correlation, when stocks fall 10%, bonds typically rise 3%, cushioning your losses."
    },
    
    "portfolio_value": {
        "short": "Current total value of all your holdings based on real-time prices.",
        "long": """
**Portfolio Value** is the sum of all your positions at current market prices.

**How it's calculated:**
For each holding: Current Price × Number of Shares
Total = Sum of all positions

**What you see:**
- **Total Value:** Current worth of your entire portfolio
- **Gain/Loss $:** Dollar change from your initial investment
- **Gain/Loss %:** Percentage return on your investment

**Example:**
- Initial investment: $100,000
- Current value: $112,500
- Gain: $12,500 (+12.5%)

**Updates:**
Prices update periodically throughout the trading day. Values shown are based on the latest available data.

**Why it matters:**
Track your progress toward financial goals and see how your investment decisions perform.
""",
        "example": "If you invested $50,000 and it's now worth $57,500, you've made $7,500 (15% return)."
    }
}


# =============================================================================
# TOOLTIP COMPONENTS
# =============================================================================

def show_tooltip(
    metric_name: str,
    show_icon: bool = True,
    position: str = "inline"
) -> None:
    """
    Display an inline tooltip with expandable explanation
    
    Args:
        metric_name: Key from TOOLTIP_CONTENT dictionary
        show_icon: Whether to show ℹ️ icon
        position: "inline" or "block" layout
    """
    
    if metric_name not in TOOLTIP_CONTENT:
        return
    
    content = TOOLTIP_CONTENT[metric_name]
    
    if position == "inline":
        # Inline tooltip with icon
        with st.expander(f"{'ℹ️ ' if show_icon else ''}What is this?", expanded=False):
            st.markdown(content['long'])
            
            if 'example' in content:
                st.info(f"**Example:** {content['example']}")
    
    else:
        # Block tooltip
        st.markdown(content['long'])
        
        if 'example' in content:
            st.info(f"**Example:** {content['example']}")


def tooltip_icon(metric_name: str, inline: bool = True) -> str:
    """
    Get tooltip content as a help text for st.metric or other components
    
    Args:
        metric_name: Key from TOOLTIP_CONTENT dictionary
        inline: If True, return short content. If False, return long content.
    
    Returns:
        Tooltip text to use in help parameter
    """
    
    if metric_name not in TOOLTIP_CONTENT:
        return ""
    
    content = TOOLTIP_CONTENT[metric_name]
    return content['short'] if inline else content['long']


def show_metric_with_tooltip(
    label: str,
    value: str,
    delta: Optional[str] = None,
    metric_key: str = None,
    delta_color: str = "normal"
) -> None:
    """
    Display a metric with an inline tooltip
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        metric_key: Key from TOOLTIP_CONTENT for tooltip
        delta_color: "normal", "inverse", or "off"
    """
    
    help_text = tooltip_icon(metric_key) if metric_key else None
    
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def show_learn_more_section(metric_name: str, expanded: bool = False) -> None:
    """
    Display a "Learn More" expandable section for a metric
    
    Args:
        metric_name: Key from TOOLTIP_CONTENT dictionary
        expanded: Whether to show expanded by default
    """
    
    if metric_name not in TOOLTIP_CONTENT:
        return
    
    content = TOOLTIP_CONTENT[metric_name]
    
    with st.expander(f"📚 Learn More: {metric_name.replace('_', ' ').title()}", expanded=expanded):
        st.markdown(content['long'])
        
        if 'example' in content:
            st.success(f"**💡 Example:** {content['example']}")


def show_quick_help_sidebar() -> None:
    """
    Display a quick help section in the sidebar with common metrics
    """
    
    with st.sidebar:
        with st.expander("❓ Metric Guide", expanded=False):
            st.markdown("""
            **Quick Reference:**
            
            - **Volatility:** How much your portfolio swings (lower = more stable)
            - **VaR:** Maximum expected daily loss (95% of the time)
            - **CVaR:** Average loss on worst days (tail risk)
            - **Sharpe Ratio:** Returns per unit of risk (higher = better)
            
            Tap any ℹ️ icon for detailed explanations.
            """)


# =============================================================================
# CONTEXTUAL HELP
# =============================================================================

def show_contextual_tip(scenario: str) -> None:
    """
    Show contextual tips based on portfolio situation
    
    Args:
        scenario: Type of tip to show ("high_volatility", "low_sharpe", etc.)
    """
    
    tips = {
        "high_volatility": {
            "icon": "⚠️",
            "title": "High Volatility Detected",
            "message": "Your portfolio has high volatility (>25%). Consider adding defensive assets like bonds (TLT, BND) or low-volatility stocks (USMV) to reduce swings.",
            "color": "#f59e0b"
        },
        "low_sharpe": {
            "icon": "📉",
            "title": "Low Risk-Adjusted Returns",
            "message": "Your Sharpe ratio is below 0.5. Consider portfolio optimization or rebalancing to improve returns relative to risk taken.",
            "color": "#ef4444"
        },
        "high_risk": {
            "icon": "🔴",
            "title": "High Risk Portfolio",
            "message": "Your worst-case loss exceeds 40%. Review your hedging strategy and consider adding defensive positions to reduce downside risk.",
            "color": "#dc2626"
        },
        "low_diversification": {
            "icon": "⚡",
            "title": "Limited Diversification",
            "message": "You have fewer than 5 holdings. Consider adding 5-10 assets from different sectors for better diversification and reduced concentration risk.",
            "color": "#f97316"
        },
        "good_portfolio": {
            "icon": "✅",
            "title": "Healthy Portfolio",
            "message": "Your portfolio shows good risk-adjusted returns and resilience. Continue monitoring regularly and maintain diversification.",
            "color": "#10b981"
        }
    }
    
    if scenario not in tips:
        return
    
    tip = tips[scenario]
    
    st.markdown(f"""
    <div style="background: {tip['color']}15; border-left: 4px solid {tip['color']}; 
                padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">{tip['icon']}</span>
            <strong style="color: {tip['color']};">{tip['title']}</strong>
        </div>
        <div style="font-size: 0.875rem; color: #6b7280; line-height: 1.5;">
            {tip['message']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Tooltip System Test", layout="wide")
    
    st.title("📚 Educational Tooltips Test")
    
    st.markdown("## Inline Tooltips")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_metric_with_tooltip(
            label="Volatility",
            value="24.5%",
            metric_key="volatility"
        )
    
    with col2:
        show_metric_with_tooltip(
            label="Sharpe Ratio",
            value="1.23",
            delta="+0.15",
            metric_key="sharpe_ratio"
        )
    
    with col3:
        show_metric_with_tooltip(
            label="CVaR (95%)",
            value="3.8%",
            metric_key="cvar"
        )
    
    st.markdown("---")
    st.markdown("## Learn More Sections")
    
    show_learn_more_section("risk_score")
    show_learn_more_section("worst_case")
    
    st.markdown("---")
    st.markdown("## Contextual Tips")
    
    show_contextual_tip("high_volatility")
    show_contextual_tip("good_portfolio")