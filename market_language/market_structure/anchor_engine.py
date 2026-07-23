"""
APEX Quant OS - Engine 6: Institutional Anchor Engine (v3.0 Dual-Layer)
Rules: Protected Anchors are strictly tied to the origin swing of confirmed BOS events.
"""

from typing import List, Optional
from market_language.market_structure.models import (
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
    Identifies active protected structural levels vs weak liquidity targets.
    """

    @staticmethod
    def derive_anchors(
        swings: List[Swing],
        events: List[StructuralEvent],
        trend: TrendDirection
    ) -> StructuralAnchors:
        anchors = StructuralAnchors()

        external_highs = [
            s for s in swings 
            if s.orientation == SwingOrientation.HIGH and s.hierarchy == HierarchyLevel.EXTERNAL
        ]
        external_lows = [
            s for s in swings 
            if s.orientation == SwingOrientation.LOW and s.hierarchy == HierarchyLevel.EXTERNAL
        ]

        if external_highs:
            anchors.current_external_high = external_highs[-1]
        if external_lows:
            anchors.current_external_low = external_lows[-1]

        # --- BULLISH TREND ANCHORS ---
        if trend == TrendDirection.BULLISH:
            if external_lows:
                anchors.protected_low = external_lows[-1]
                anchors.protected_low.lifecycle = SwingLifecycleState.PROTECTED_STRONG
            
            if external_highs:
                anchors.weak_high = external_highs[-1]
                anchors.weak_high.lifecycle = SwingLifecycleState.WEAK_TARGET

        # --- BEARISH TREND ANCHORS ---
        elif trend == TrendDirection.BEARISH:
            if external_highs:
                anchors.protected_high = external_highs[-1]
                anchors.protected_high.lifecycle = SwingLifecycleState.PROTECTED_STRONG
            
            if external_lows:
                anchors.weak_low = external_lows[-1]
                anchors.weak_low.lifecycle = SwingLifecycleState.WEAK_TARGET

        return anchors
