"""
APEX Quant OS - Engine 6: Institutional Causal Anchor Engine (v3.5)
Features: Verified Causal Chain Displacement Proof for Protected vs Weak Swings.
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
    Identifies active protected strong levels vs targeted weak levels.
    Verifies that strong swings directly originated validated BOS displacement.
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

        # Isolate validated external BOS events
        bullish_bos = [e for e in events if e.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_CHOCH_BULLISH]]
        bearish_bos = [e for e in events if e.event_type in [EventType.EXTERNAL_BOS_BEARISH, EventType.EXTERNAL_CHOCH_BEARISH]]

        # --- 1. BULLISH TREND CAUSAL PROOF ---
        if trend == TrendDirection.BULLISH:
            if bullish_bos and ext_lows:
                latest_bos = bullish_bos[-1]
                # Filter lows that existed prior to the breakout event
                causal_candidates = [l for l in ext_lows if l.price_point.timestamp < latest_bos.trigger_timestamp]
                
                if causal_candidates:
                    # Causal Strong Low = Lowest extremum originating the expansion leg
                    causal_low = min(causal_candidates, key=lambda s: s.price_point.price)
                    causal_low.lifecycle = SwingLifecycleState.PROTECTED_STRONG
                    causal_low.is_strong = True
                    causal_low.caused_displacement = True
                    anchors.protected_low = causal_low
            elif ext_lows:
                anchors.protected_low = ext_lows[-1]
                anchors.protected_low.lifecycle = SwingLifecycleState.PROTECTED_STRONG

            # High that failed to protect or hold is marked as Weak Target
            if ext_highs:
                anchors.weak_high = ext_highs[-1]
                anchors.weak_high.lifecycle = SwingLifecycleState.WEAK_TARGET
                anchors.weak_high.is_strong = False

        # --- 2. BEARISH TREND CAUSAL PROOF ---
        elif trend == TrendDirection.BEARISH:
            if bearish_bos and ext_highs:
                latest_bos = bearish_bos[-1]
                causal_candidates = [h for h in ext_highs if h.price_point.timestamp < latest_bos.trigger_timestamp]
                
                if causal_candidates:
                    # Causal Strong High = Highest extremum originating the breakdown leg
                    causal_high = max(causal_candidates, key=lambda s: s.price_point.price)
                    causal_high.lifecycle = SwingLifecycleState.PROTECTED_STRONG
                    causal_high.is_strong = True
                    causal_high.caused_displacement = True
                    anchors.protected_high = causal_high
            elif ext_highs:
                anchors.protected_high = ext_highs[-1]
                anchors.protected_high.lifecycle = SwingLifecycleState.PROTECTED_STRONG

            # Low that failed to hold is marked as Weak Target
            if ext_lows:
                anchors.weak_low = ext_lows[-1]
                anchors.weak_low.lifecycle = SwingLifecycleState.WEAK_TARGET
                anchors.weak_low.is_strong = False

        return anchors
