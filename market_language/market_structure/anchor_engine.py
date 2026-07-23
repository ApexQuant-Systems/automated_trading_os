"""
APEX Quant OS - Engine 6: Institutional Causal Anchor Engine (v3.2)
Rules: 
- Causal Strong Anchor = Exact lowest/highest price point that originated the displacement leg causing an External BOS.
- Weak Target Anchor = Liquidity target that failed to create displacement.
"""

from typing import List, Optional
from market_language.market_structure.models import (
    EventType,
    HierarchyLevel,
    StructuralAnchors,
    StructuralEvent,
    Swing,
    SwingLifecycleState,
    SwingOrientation,
    TrendDirection,
)


class AnchorEngine:
    """
    Identifies active protected strong levels vs targeted weak levels based on causal displacement origin.
    """

    @staticmethod
    def derive_anchors(
        swings: List[Swing],
        events: List[StructuralEvent],
        trend: TrendDirection
    ) -> StructuralAnchors:
        anchors = StructuralAnchors()

        ext_highs = [s for s in swings if s.orientation == SwingOrientation.HIGH and s.hierarchy == HierarchyLevel.EXTERNAL]
        ext_lows = [s for s in swings if s.orientation == SwingOrientation.LOW and s.hierarchy == HierarchyLevel.EXTERNAL]

        if ext_highs:
            anchors.current_external_high = ext_highs[-1]
        if ext_lows:
            anchors.current_external_low = ext_lows[-1]

        # Isolate external BOS events
        bullish_bos = [e for e in events if e.event_type == EventType.EXTERNAL_BOS_BULLISH]
        bearish_bos = [e for e in events if e.event_type == EventType.EXTERNAL_BOS_BEARISH]

        # --- BULLISH TREND CAUSAL ANCHOR LOGIC ---
        if trend == TrendDirection.BULLISH:
            if bullish_bos and ext_lows:
                latest_bos = bullish_bos[-1]
                # Find all external lows that occurred BEFORE the BOS trigger timestamp
                prior_lows = [l for l in ext_lows if l.price_point.timestamp <= latest_bos.trigger_timestamp]
                
                if prior_lows:
                    # Causal Origin = The lowest swing before the breakout
                    causal_low = min(prior_lows, key=lambda s: s.price_point.price)
                    anchors.protected_low = causal_low
                    causal_low.lifecycle = SwingLifecycleState.PROTECTED_STRONG
                    causal_low.is_strong = True
            elif ext_lows:
                anchors.protected_low = ext_lows[-1]
                anchors.protected_low.lifecycle = SwingLifecycleState.PROTECTED_STRONG

            if ext_highs:
                anchors.weak_high = ext_highs[-1]
                anchors.weak_high.lifecycle = SwingLifecycleState.WEAK_TARGET

        # --- BEARISH TREND CAUSAL ANCHOR LOGIC ---
        elif trend == TrendDirection.BEARISH:
            if bearish_bos and ext_highs:
                latest_bos = bearish_bos[-1]
                prior_highs = [h for h in ext_highs if h.price_point.timestamp <= latest_bos.trigger_timestamp]
                
                if prior_highs:
                    # Causal Origin = The highest swing before the breakdown
                    causal_high = max(prior_highs, key=lambda s: s.price_point.price)
                    anchors.protected_high = causal_high
                    causal_high.lifecycle = SwingLifecycleState.PROTECTED_STRONG
                    causal_high.is_strong = True
            elif ext_highs:
                anchors.protected_high = ext_highs[-1]
                anchors.protected_high.lifecycle = SwingLifecycleState.PROTECTED_STRONG

            if ext_lows:
                anchors.weak_low = ext_lows[-1]
                anchors.weak_low.lifecycle = SwingLifecycleState.WEAK_TARGET

        return anchors
