# utils/hedge_preview.py
"""
Hedge Preview Component
Shows before/after comparison when adding a hedge to portfolio
Uses Streamlit's native components for better compatibility
NOW WITH EDUCATIONAL TOOLTIPS!
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional
from utils.tooltips import tooltip_icon

def show_hedge_preview_dialog(
    hedge_symbol: str,
    hedge_name: str,
    hedge_description: str,
    current_symbols: List[str],
    current_weights: List[float],
    hedge_weight: float = 0.10
) -> Tuple[bool, bool]:
    """
    Show hedge preview with before/after comparison in Streamlit container
    
    Args:
        hedge_symbol: Symbol of hedge (e.g., "TLT")
        hedge_name: Display name (e.g., "20+ Year Treasury Bonds")
        hedge_description: Short description
        current_symbols: Current portfolio symbols
        current_weights: Current portfolio weights
        hedge_weight: Allocation for hedge (default 10%)
    
    Returns:
        Tuple of (show_dialog, confirmed)
        - show_dialog: Whether dialog should be shown
        - confirmed: Whether user confirmed adding the hedge
    """
    
    preview_key = f"hedge_preview_{hedge_symbol}"
    
    # Check if this hedge preview should be shown
    if not st.session_state.get(f"{preview_key}_active", False):
        return False, False
    
    # Show preview in a prominent container
    st.markdown("---")
    st.markdown(f"### 🔍 Preview: Adding {hedge_symbol}")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    ">
        <div style="font-size: 1.125rem; font-weight: bold; margin-bottom: 0.5rem;">
            {hedge_name}
        </div>
        <div style="font-size: 0.875rem; opacity: 0.9;">
            {hedge_description}
        </div>
        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.3);">
            <strong>Allocation:</strong> {hedge_weight*100:.0f}% to {hedge_symbol}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate projected portfolio
    try:
        from utils.api_client import get_api_client
        
        client = get_api_client()
        
        with st.spinner("Calculating impact..."):
            # Get current risk metrics
            symbols_tuple = tuple(current_symbols)
            weights_tuple = tuple(current_weights)
            
            current_risk = client.get_risk_analysis(symbols_tuple, weights_tuple)
            
            # Evaluate hedge
            hedge_eval = client.evaluate_hedge(
                symbols_tuple,
                weights_tuple,
                hedge_symbol,
                hedge_weight
            )
            
            if 'error' in hedge_eval:
                st.error(f"Unable to evaluate hedge: {hedge_eval['error']}")
                if st.button("Close", key=f"{preview_key}_close_error"):
                    st.session_state[f"{preview_key}_active"] = False
                    st.rerun()
                return True, False
            
            # Extract metrics
            current_metrics = current_risk.get('metrics', {})

            # Get hedge evaluation data
            hedge_data = hedge_eval.get('hedge_evaluation', {})
            before = hedge_data.get('current_metrics', {})
            after = hedge_data.get('hedged_metrics', {})

            # Display comparison
            st.markdown("### 📊 Before vs After")

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.markdown("**Current Portfolio**")
            with col2:
                st.markdown("**With Hedge**")
            with col3:
                st.markdown("**Δ Change**")

            st.markdown("---")

            # ========================================================================
            # VOLATILITY COMPARISON - WITH TOOLTIPS
            # ========================================================================
            current_vol_raw = before.get('volatility', current_metrics.get('annualized_volatility', 0))
            hedge_vol_raw = after.get('volatility', current_vol_raw)

            current_vol = current_vol_raw * 100
            hedge_vol = hedge_vol_raw * 100
            vol_diff = hedge_vol - current_vol

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.metric(
                    "Volatility", 
                    f"{current_vol:.1f}%",
                    help=tooltip_icon("volatility")  # NEW: Tooltip
                )
            with col2:
                st.metric(
                    "Volatility", 
                    f"{hedge_vol:.1f}%", 
                    delta=f"{vol_diff:.1f}%", 
                    delta_color="inverse",
                    help="Lower volatility = more stable portfolio"  # NEW: Context
                )
            with col3:
                if vol_diff < 0:
                    st.markdown("✅", help="Lower is better")
                else:
                    st.markdown("⚠️", help="Higher volatility")

            # ========================================================================
            # CVAR COMPARISON - WITH TOOLTIPS
            # ========================================================================
            current_cvar_raw = before.get('cvar_95', current_metrics.get('portfolio_cvar_95', current_metrics.get('cvar_95', 0)))
            hedge_cvar_raw = after.get('cvar_95', current_cvar_raw)

            current_cvar = abs(current_cvar_raw) * 100
            hedge_cvar = abs(hedge_cvar_raw) * 100
            cvar_diff = hedge_cvar - current_cvar

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.metric(
                    "Tail Risk (CVaR)", 
                    f"{current_cvar:.1f}%",
                    help=tooltip_icon("cvar")  # NEW: Tooltip
                )
            with col2:
                st.metric(
                    "Tail Risk (CVaR)", 
                    f"{hedge_cvar:.1f}%", 
                    delta=f"{cvar_diff:.1f}%", 
                    delta_color="inverse",
                    help="Lower CVaR = better crash protection"  # NEW: Context
                )
            with col3:
                if cvar_diff < 0:
                    st.markdown("✅", help="Lower is better")
                else:
                    st.markdown("⚠️", help="Higher tail risk")

            # ========================================================================
            # SHARPE RATIO COMPARISON - WITH TOOLTIPS
            # ========================================================================
            current_sharpe = before.get('sharpe_ratio', current_metrics.get('sharpe_ratio', 0))
            hedge_sharpe = after.get('sharpe_ratio', current_sharpe)
            sharpe_diff = hedge_sharpe - current_sharpe
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.metric(
                    "Sharpe Ratio", 
                    f"{current_sharpe:.2f}",
                    help=tooltip_icon("sharpe_ratio")  # NEW: Tooltip
                )
            with col2:
                st.metric(
                    "Sharpe Ratio", 
                    f"{hedge_sharpe:.2f}", 
                    delta=f"{sharpe_diff:+.2f}",
                    help="Higher Sharpe = better risk-adjusted returns"  # NEW: Context
                )
            with col3:
                if sharpe_diff > 0:
                    st.markdown("✅", help="Better risk-adjusted returns")
                else:
                    st.markdown("⚠️", help="Lower risk-adjusted returns")
            
            # ========================================================================
            # NEW: EDUCATIONAL SECTION - Understanding Metrics
            # ========================================================================
            with st.expander("📚 Understanding These Metrics"):
                st.markdown("""
                ## What Do These Changes Mean?
                
                **Volatility:**
                - **Lower = Good** for stability
                - Adding bonds/defensive assets typically reduces volatility
                - Trade-off: Usually means lower returns in bull markets
                
                **CVaR (Tail Risk):**
                - **Lower = Better** crash protection
                - Shows how badly you get hurt in worst 5% of days
                - Hedges like TLT, GLD specifically target tail risk
                
                **Sharpe Ratio:**
                - **Higher = Better** risk-adjusted returns
                - Measures efficiency: return per unit of risk
                - Can go down if hedge has lower returns than portfolio
                
                ## The Hedge Trade-off
                
                Most hedges provide **protection** (lower volatility & CVaR) but may reduce **efficiency** (lower Sharpe).
                
                **This is normal and expected!**
                
                You're exchanging some upside potential for downside protection. 
                Whether this trade-off is worth it depends on your risk tolerance and market outlook.
                
                ### Examples:
                - **TLT (Treasury Bonds):** Great crash protection, but lower returns
                - **GLD (Gold):** Inflation hedge, moves independently of stocks
                - **BND (Total Bonds):** Broad bond exposure, moderate protection
                
                **Tip:** Look for hedges that reduce CVaR more than they reduce Sharpe!
                """)
            
            # Summary insights
            st.markdown("---")
            st.markdown("### 💡 Summary")
            
            improvements = []
            concerns = []
            
            if vol_diff < -1.0:
                improvements.append("**Significantly reduces volatility** - Your portfolio will be more stable")
            elif vol_diff < 0:
                improvements.append("**Reduces volatility** - Slightly more stable portfolio")
            else:
                concerns.append("**Increases volatility** - Portfolio becomes more volatile")
            
            if cvar_diff < -0.5:
                improvements.append("**Lowers tail risk** - Better protection in worst-case scenarios")
            elif cvar_diff > 0.5:
                concerns.append("**Increases tail risk** - Worse performance in crisis scenarios")
            
            if sharpe_diff > 0.1:
                improvements.append("**Improves risk-adjusted returns** - Better return per unit of risk")
            elif sharpe_diff < -0.1:
                concerns.append("**Reduces risk-adjusted returns** - Lower return per unit of risk")
            
            if improvements:
                st.success("**Benefits:**\n\n" + "\n\n".join(f"✓ {imp}" for imp in improvements))
            
            if concerns:
                st.warning("**Trade-offs:**\n\n" + "\n\n".join(f"⚠️ {con}" for con in concerns))
            
            if not improvements and not concerns:
                st.info("**Neutral Impact:** This hedge has minimal effect on your portfolio metrics.")
            
            # New allocation breakdown
            with st.expander("📋 New Portfolio Allocation"):
                st.markdown("**After adding hedge:**")
                
                # Calculate new weights
                scale_factor = 1 - hedge_weight
                new_allocations = []
                
                for symbol, weight in zip(current_symbols, current_weights):
                    new_weight = weight * scale_factor
                    new_allocations.append((symbol, new_weight))
                
                new_allocations.append((hedge_symbol, hedge_weight))
                
                for symbol, weight in new_allocations:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{symbol}**")
                    with col2:
                        st.write(f"{weight*100:.1f}%")
            
            # Action buttons
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("❌ Cancel", key=f"{preview_key}_cancel", use_container_width=True):
                    st.session_state[f"{preview_key}_active"] = False
                    st.rerun()
            
            with col2:
                if st.button(f"✅ Add {hedge_symbol}", key=f"{preview_key}_confirm", use_container_width=True, type="primary"):
                    st.session_state[f"{preview_key}_active"] = False
                    st.session_state[f"{preview_key}_confirmed"] = True
                    return True, True
            
            return True, False
            
    except Exception as e:
        st.error(f"Unable to calculate hedge impact: {str(e)}")
        if st.button("Close", key=f"{preview_key}_close"):
            st.session_state[f"{preview_key}_active"] = False
            st.rerun()
        return True, False

def activate_hedge_preview(hedge_symbol: str):
    """Activate the hedge preview for a specific symbol"""
    preview_key = f"hedge_preview_{hedge_symbol}"
    st.session_state[f"{preview_key}_active"] = True

def is_hedge_confirmed(hedge_symbol: str) -> bool:
    """Check if hedge was confirmed and clear the flag"""
    preview_key = f"hedge_preview_{hedge_symbol}"
    confirmed = st.session_state.get(f"{preview_key}_confirmed", False)
    if confirmed:
        st.session_state[f"{preview_key}_confirmed"] = False
    return confirmed