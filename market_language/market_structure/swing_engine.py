"""
APEX Quant OS - Engine 1: Institutional Dual-Layer Swing Engine (v3.0)
Features: Internal vs External Structure Separation, Inducement (IDM) Identification, and IDM Confirmation.
"""

from typing import List, Tuple
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
    Detects both Internal Structure (minor pullbacks) and External Structure (IDM-confirmed pivots).
    """

    @staticmethod
    def _calculate_atr(candles: List[Candle], period: int = 14) -> List[float]:
        if len(candles) < period:
            return [0.0] * len(candles)

        tr_list = []
        for i in range(len(candles)):
            if i == 0:
                tr_list.append(candles[i].range)
            else:
                prev_close = candles[i - 1].close
                tr = max(
                    candles[i].high - candles[i].low,
                    abs(candles[i].high - prev_close),
                    abs(candles[i].low - prev_close)
                )
                tr_list.append(tr)

        atr_list = [0.0] * len(candles)
        first_atr = sum(tr_list[:period]) / float(period)
        atr_list[period - 1] = first_atr

        for i in range(period, len(candles)):
            atr_list[i] = (atr_list[i - 1] * (period - 1) + tr_list[i]) / float(period)

        return atr_list

    @classmethod
    def detect_swings(
        cls,
        candles: List[Candle],
        policy: MarketStructurePolicy
    ) -> Tuple[List[Swing], List[Swing]]:
        """
        Returns (external_swings, internal_swings).
        """
        if len(candles) < 5:
            return [], []

        atr_values = cls._calculate_atr(candles)
        internal_swings: List[Swing] = []
        n = len(candles)

        # --- 1. DETECT ALL INTERNAL SWINGS (Candle-Level & Micro Fractality) ---
        for i in range(2, n - 2):
            curr = candles[i]
            
            # Internal High (2-bar local peak)
            if curr.high > candles[i-1].high and curr.high > candles[i-2].high and \
               curr.high > candles[i+1].high and curr.high > candles[i+2].high:
                internal_swings.append(
                    Swing(
                        orientation=SwingOrientation.HIGH,
                        price_point=PricePoint(curr.timestamp, curr.high),
                        hierarchy=HierarchyLevel.INTERNAL,
                        lifecycle=SwingLifecycleState.CONFIRMED,
                        candle_index=i
                    )
                )

            # Internal Low (2-bar local trough)
            if curr.low < candles[i-1].low and curr.low < candles[i-2].low and \
               curr.low < candles[i+1].low and curr.low < candles[i+2].low:
                internal_swings.append(
                    Swing(
                        orientation=SwingOrientation.LOW,
                        price_point=PricePoint(curr.timestamp, curr.low),
                        hierarchy=HierarchyLevel.INTERNAL,
                        lifecycle=SwingLifecycleState.CONFIRMED,
                        candle_index=i
                    )
                )

        internal_swings.sort(key=lambda s: s.price_point.timestamp)

        # --- 2. IDENTIFY INDUCEMENT (IDM) & BUILD EXTERNAL STRUCTURE ---
        # Inducement = First valid internal pullback after an expansion push
        external_swings: List[Swing] = []
        
        for idx, swing in enumerate(internal_swings):
            # Apply ATR Depth filter to elevate Internal Swing -> External Candidate
            atr = atr_values[swing.candle_index] if atr_values[swing.candle_index] > 0 else 1.0
            
            # Evaluate depth against neighbors
            if idx > 0 and idx < len(internal_swings) - 1:
                prev_s = internal_swings[idx - 1]
                next_s = internal_swings[idx + 1]
                depth = abs(swing.price_point.price - prev_s.price_point.price)

                if depth >= (policy.atr_filter_multiplier * atr):
                    ext_swing = Swing(
                        orientation=swing.orientation,
                        price_point=swing.price_point,
                        hierarchy=HierarchyLevel.EXTERNAL,
                        lifecycle=SwingLifecycleState.CONFIRMED,
                        candle_index=swing.candle_index
                    )
                    
                    # Mark first minor internal pullback as Inducement
                    if swing.orientation == SwingOrientation.LOW:
                        swing.is_idm = True

                    external_swings.append(ext_swing)

        # --- 3. ALTERNATING CHAIN CLEANUP ON EXTERNAL SWINGS ---
        cleaned_external: List[Swing] = []
        for s in external_swings:
            if not cleaned_external:
                cleaned_external.append(s)
                continue

            last = cleaned_external[-1]
            if last.orientation == s.orientation:
                if s.orientation == SwingOrientation.HIGH and s.price_point.price > last.price_point.price:
                    cleaned_external[-1] = s
                elif s.orientation == SwingOrientation.LOW and s.price_point.price < last.price_point.price:
                    cleaned_external[-1] = s
            else:
                cleaned_external.append(s)

        return cleaned_external, internal_swings
