"""
APEX Quant OS - Engine 3: Institutional Event Engine (v2.2)
Fixes: Debounced Structural Rejections (Wick Sweeps) to prevent event flooding.
"""

from typing import List, Tuple, Set
from market_language.market_structure.models import (
    Candle,
    EventType,
    HierarchyLevel,
    StructuralEvent,
    Swing,
    SwingLifecycleState,
    SwingOrientation,
    TrendDirection,
)
from market_language.market_structure.policy import MarketStructurePolicy


class EventEngine:
    """
    Evaluates candle price action against active swings to generate immutable StructuralEvent objects.
    Enforces displacement buffers, debounces wick sweeps, and differentiates true breaks.
    """

    @staticmethod
    def _calculate_atr_simple(candles: List[Candle], index: int, period: int = 14) -> float:
        if index < period:
            return candles[index].range if candles else 1.0
        subset = candles[index - period:index]
        return sum(c.range for c in subset) / float(period)

    @classmethod
    def detect_events(
        cls,
        candles: List[Candle],
        swings: List[Swing],
        current_trend: TrendDirection,
        policy: MarketStructurePolicy
    ) -> Tuple[List[StructuralEvent], List[Swing]]:
        events: List[StructuralEvent] = []
        swept_swing_ids: Set[str] = set()
        
        active_highs = [
            s for s in swings 
            if s.orientation == SwingOrientation.HIGH 
            and s.lifecycle in [SwingLifecycleState.CONFIRMED, SwingLifecycleState.PROTECTED, SwingLifecycleState.WEAK]
        ]
        active_lows = [
            s for s in swings 
            if s.orientation == SwingOrientation.LOW 
            and s.lifecycle in [SwingLifecycleState.CONFIRMED, SwingLifecycleState.PROTECTED, SwingLifecycleState.WEAK]
        ]

        for idx, candle in enumerate(candles):
            atr = cls._calculate_atr_simple(candles, idx)
            buffer = policy.equal_price_tolerance_pct * atr

            # --- 1. EVALUATE HIGHS ---
            for swing_high in list(active_highs):
                if candle.timestamp <= swing_high.price_point.timestamp:
                    continue

                level = swing_high.price_point.price

                # Body Close Break (BOS / CHOCH)
                if candle.close > (level + buffer):
                    if swing_high.hierarchy == HierarchyLevel.INTERNAL:
                        evt_type = EventType.MSS_BULLISH
                    elif current_trend == TrendDirection.BULLISH:
                        evt_type = EventType.BOS_BULLISH
                    else:
                        evt_type = EventType.CHOCH_BULLISH

                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=swing_high.id,
                            confidence=swing_high.confidence
                        )
                    )
                    swing_high.lifecycle = SwingLifecycleState.BROKEN
                    active_highs.remove(swing_high)

                # Wick Sweep (Structural Rejection) - Debounced (Triggered ONCE per swing)
                elif candle.high > level and candle.close <= level:
                    if swing_high.id not in swept_swing_ids:
                        events.append(
                            StructuralEvent(
                                event_type=EventType.STRUCTURAL_REJECTION,
                                trigger_timestamp=candle.timestamp,
                                trigger_price=candle.high,
                                broken_swing_id=swing_high.id,
                                confidence=0.8
                            )
                        )
                        swept_swing_ids.add(swing_high.id)

            # --- 2. EVALUATE LOWS ---
            for swing_low in list(active_lows):
                if candle.timestamp <= swing_low.price_point.timestamp:
                    continue

                level = swing_low.price_point.price

                # Body Close Break (BOS / CHOCH)
                if candle.close < (level - buffer):
                    if swing_low.hierarchy == HierarchyLevel.INTERNAL:
                        evt_type = EventType.MSS_BEARISH
                    elif current_trend == TrendDirection.BEARISH:
                        evt_type = EventType.BOS_BEARISH
                    else:
                        evt_type = EventType.CHOCH_BEARISH

                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=swing_low.id,
                            confidence=swing_low.confidence
                        )
                    )
                    swing_low.lifecycle = SwingLifecycleState.BROKEN
                    active_lows.remove(swing_low)

                # Wick Sweep (Structural Rejection) - Debounced (Triggered ONCE per swing)
                elif candle.low < level and candle.close >= level:
                    if swing_low.id not in swept_swing_ids:
                        events.append(
                            StructuralEvent(
                                event_type=EventType.STRUCTURAL_REJECTION,
                                trigger_timestamp=candle.timestamp,
                                trigger_price=candle.low,
                                broken_swing_id=swing_low.id,
                                confidence=0.8
                            )
                        )
                        swept_swing_ids.add(swing_low.id)

        return events, swings
