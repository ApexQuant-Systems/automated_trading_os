"""
APEX Quant OS - Engine 1: Institutional Swing Engine (v2.1)
Features: Inside-Bar Compression, ATR Depth Filtering, and Alternating Peak/Trough Chain Enforcement.
"""

from typing import List
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
    Production-grade swing detection engine that filters out market noise,
    inside bars, and low-volatility consolidation.
    """

    @staticmethod
    def _calculate_atr(candles: List[Candle], period: int = 14) -> List[float]:
        """Computes Average True Range for volatility filtering."""
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
        # First ATR is simple moving average of TR
        first_atr = sum(tr_list[:period]) / float(period)
        atr_list[period - 1] = first_atr

        # Wilder's Smoothing
        for i in range(period, len(candles)):
            atr_list[i] = (atr_list[i - 1] * (period - 1) + tr_list[i]) / float(period)

        return atr_list

    @classmethod
    def detect_swings(
        cls,
        candles: List[Candle],
        policy: MarketStructurePolicy,
        hierarchy: HierarchyLevel = HierarchyLevel.EXTERNAL
    ) -> List[Swing]:
        left = policy.fractal_left_bars
        right = policy.fractal_right_bars
        if len(candles) < (left + right + 1):
            return []

        atr_values = cls._calculate_atr(candles)
        raw_swings: List[Swing] = []
        n = len(candles)

        # --- STAGE 1 & 2: FRACTAL DETECTION + ATR DEPTH FILTER ---
        for i in range(left, n - right):
            current = candles[i]
            atr = atr_values[i] if atr_values[i] > 0 else (current.range or 1.0)
            
            # Source extraction
            if policy.extrema_source == "WICKS":
                curr_high = current.high
                curr_low = current.low
                get_high = lambda c: c.high
                get_low = lambda c: c.low
            else:
                curr_high = max(current.open, current.close)
                curr_low = min(current.open, current.close)
                get_high = lambda c: max(c.open, c.close)
                get_low = lambda c: min(c.open, c.close)

            # Check Fractal High
            is_high = True
            for j in range(i - left, i + right + 1):
                if i == j:
                    continue
                if get_high(candles[j]) >= curr_high:
                    is_high = False
                    break

            if is_high:
                # Apply ATR Depth Filter if enabled
                depth = curr_high - min(get_low(candles[i - left]), get_low(candles[i + right]))
                if policy.atr_filter_multiplier == 0 or depth >= (policy.atr_filter_multiplier * atr):
                    raw_swings.append(
                        Swing(
                            orientation=SwingOrientation.HIGH,
                            price_point=PricePoint(timestamp=current.timestamp, price=curr_high),
                            hierarchy=hierarchy,
                            lifecycle=SwingLifecycleState.CONFIRMED,
                            candle_index=i,
                            confidence=1.0
                        )
                    )

            # Check Fractal Low
            is_low = True
            for j in range(i - left, i + right + 1):
                if i == j:
                    continue
                if get_low(candles[j]) <= curr_low:
                    is_low = False
                    break

            if is_low:
                depth = max(get_high(candles[i - left]), get_high(candles[i + right])) - curr_low
                if policy.atr_filter_multiplier == 0 or depth >= (policy.atr_filter_multiplier * atr):
                    raw_swings.append(
                        Swing(
                            orientation=SwingOrientation.LOW,
                            price_point=PricePoint(timestamp=current.timestamp, price=curr_low),
                            hierarchy=hierarchy,
                            lifecycle=SwingLifecycleState.CONFIRMED,
                            candle_index=i,
                            confidence=1.0
                        )
                    )

        # Sort chronologically
        raw_swings.sort(key=lambda s: s.price_point.timestamp)

        # --- STAGE 3: ALTERNATING CHAIN ENFORCEMENT ---
        # Ensures structure strictly alternates: High -> Low -> High -> Low
        if not raw_swings:
            return []

        cleaned_swings: List[Swing] = []
        for s in raw_swings:
            if not cleaned_swings:
                cleaned_swings.append(s)
                continue

            last = cleaned_swings[-1]
            if last.orientation == s.orientation:
                # Consecutive identical orientation: keep only the most extreme level
                if s.orientation == SwingOrientation.HIGH:
                    if s.price_point.price > last.price_point.price:
                        cleaned_swings[-1] = s # Replace with higher high
                else:
                    if s.price_point.price < last.price_point.price:
                        cleaned_swings[-1] = s # Replace with lower low
            else:
                cleaned_swings.append(s)

        return cleaned_swings
