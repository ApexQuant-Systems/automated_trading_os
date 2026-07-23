"""
APEX Quant OS - Engine 6: Anchor Engine
Maintains active structural anchors, assigning Protected High/Low and Weak High/Low designations.
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
    Identifies active protected levels and targeted weak boundaries based on trend direction.
    """

    @staticmethod
    def derive_anchors(
        swings: List[Swing],
        events: List[StructuralEvent],
        trend: TrendDirection
    ) -> StructuralAnchors:
        """
        Computes active protected and weak anchors.
        """
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

        # --- ASSIGN PROTECTED / WEAK ANCHORS ---
        if trend == TrendDirection.BULLISH:
            # In a Bullish trend, the low that caused the break is PROTECTED.
            # The high being targeted is WEAK.
            anchors.protected_low = anchors.current_external_low
            if anchors.protected_low:
                anchors.protected_low.lifecycle = SwingLifecycleState.PROTECTED

            anchors.weak_high = anchors.current_external_high
            if anchors.weak_high:
                anchors.weak_high.lifecycle = SwingLifecycleState.WEAK

        elif trend == TrendDirection.BEARISH:
            # In a Bearish trend, the high that caused the break is PROTECTED.
            # The low being targeted is WEAK.
            anchors.protected_high = anchors.current_external_high
            if anchors.protected_high:
                anchors.protected_high.lifecycle = SwingLifecycleState.PROTECTED

            anchors.weak_low = anchors.current_external_low
            if anchors.weak_low:
                anchors.weak_low.lifecycle = SwingLifecycleState.WEAK

        return anchors
