"""
APEX Quant OS - Engine 1: Swing Engine
Detects local extrema wicks/bodies, manages inside-bar policies, and assigns structural hierarchy.
"""

from typing import List, Optional
from market_language.market_structure.models import (
    Candle,
    HierarchyLevel,
    PricePoint,
    Swing,
    SwingLifecycleState,
    SwingOrientation,
)
from market_language.market_structure.policy import MarketStructurePolicy


class SwingEngine:
    """
    Identifies fractal swings from a sequence of candles using configurable N-bar window rules.
    """

    @staticmethod
    def detect_swings(
        candles: List[Candle],
        policy: MarketStructurePolicy,
        hierarchy: HierarchyLevel = HierarchyLevel.EXTERNAL
    ) -> List[Swing]:
        """
        Scans candle history and returns confirmed Swing objects.
        """
        if len(candles) < (policy.fractal_left_bars + policy.fractal_right_bars + 1):
            return []

        swings: List[Swing] = []
        left = policy.fractal_left_bars
        right = policy.fractal_right_bars
        n = len(candles)

        for i in range(left, n - right):
            current = candles[i]
            
            # --- EXTRACT HIGH/LOW BASED ON POLICY ---
            if policy.extrema_source == "WICKS":
                get_high = lambda c: c.high
                get_low = lambda c: c.low
            else:
                get_high = lambda c: max(c.open, c.close)
                get_low = lambda c: min(c.open, c.close)

            curr_high = get_high(current)
            curr_low = get_low(current)

            # Check Swing High
            is_swing_high = True
            for j in range(i - left, i + right + 1):
                if i == j:
                    continue
                if get_high(candles[j]) >= curr_high:
                    is_swing_high = False
                    break

            if is_swing_high:
                swings.append(
                    Swing(
                        orientation=SwingOrientation.HIGH,
                        price_point=PricePoint(timestamp=current.timestamp, price=curr_high),
                        hierarchy=hierarchy,
                        lifecycle=SwingLifecycleState.CONFIRMED,
                        candle_index=i,
                        confidence=1.0
                    )
                )

            # Check Swing Low
            is_swing_low = True
            for j in range(i - left, i + right + 1):
                if i == j:
                    continue
                if get_low(candles[j]) <= curr_low:
                    is_swing_low = False
                    break

            if is_swing_low:
                swings.append(
                    Swing(
                        orientation=SwingOrientation.LOW,
                        price_point=PricePoint(timestamp=current.timestamp, price=curr_low),
                        hierarchy=hierarchy,
                        lifecycle=SwingLifecycleState.CONFIRMED,
                        candle_index=i,
                        confidence=1.0
                    )
                )

        return sorted(swings, key=lambda s: s.price_point.timestamp)
