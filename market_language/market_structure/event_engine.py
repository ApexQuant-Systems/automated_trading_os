"""
APEX Quant OS - Engine 3: Event Engine
Detects structural breakouts (BOS, CHOCH, MSS) based on active candle expansion and break policy.
"""

from typing import List, Optional, Tuple
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
    """

    @staticmethod
    def detect_events(
        candles: List[Candle],
        swings: List[Swing],
        current_trend: TrendDirection,
        policy: MarketStructurePolicy
    ) -> Tuple[List[StructuralEvent], List[Swing]]:
        """
        Scans price expansion past active swings. Marks broken swings as BROKEN and returns new events.
        """
        events: List[StructuralEvent] = []
        
        # Filter active confirmed swings
        active_highs = [
            s for s in swings 
            if s.orientation == SwingOrientation.HIGH and s.lifecycle in [SwingLifecycleState.CONFIRMED, SwingLifecycleState.PROTECTED, SwingLifecycleState.WEAK]
        ]
        active_lows = [
            s for s in swings 
            if s.orientation == SwingOrientation.LOW and s.lifecycle in [SwingLifecycleState.CONFIRMED, SwingLifecycleState.PROTECTED, SwingLifecycleState.WEAK]
        ]

        for candle in candles:
            # --- EVALUATE BREAK OF HIGHS ---
            for swing_high in list(active_highs):
                if candle.timestamp <= swing_high.price_point.timestamp:
                    continue

                level = swing_high.price_point.price
                break_triggered = False

                if policy.break_confirmation == "STRICT_BODY":
                    break_triggered = candle.close > level
                elif policy.break_confirmation == "AGGRESSIVE_WICK":
                    break_triggered = candle.high > level

                if break_triggered:
                    # Classify Event Type (BOS vs CHOCH vs MSS)
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
                            trigger_price=candle.close if policy.break_confirmation == "STRICT_BODY" else candle.high,
                            broken_swing_id=swing_high.id,
                            confidence=swing_high.confidence
                        )
                    )
                    swing_high.lifecycle = SwingLifecycleState.BROKEN
                    active_highs.remove(swing_high)

            # --- EVALUATE BREAK OF LOWS ---
            for swing_low in list(active_lows):
                if candle.timestamp <= swing_low.price_point.timestamp:
                    continue

                level = swing_low.price_point.price
                break_triggered = False

                if policy.break_confirmation == "STRICT_BODY":
                    break_triggered = candle.close < level
                elif policy.break_confirmation == "AGGRESSIVE_WICK":
                    break_triggered = candle.low < level

                if break_triggered:
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
                            trigger_price=candle.close if policy.break_confirmation == "STRICT_BODY" else candle.low,
                            broken_swing_id=swing_low.id,
                            confidence=swing_low.confidence
                        )
                    )
                    swing_low.lifecycle = SwingLifecycleState.BROKEN
                    active_lows.remove(swing_low)

        return events, swings
