"""
APEX Quant OS - Engine 4: Institutional Trend Engine (v2.1)
Features: Reversal validation (CHOCH), Failure Swings (SMS), and Trend Maturity tracking.
"""

from typing import List, Optional
from market_language.market_structure.models import (
    EventType,
    StructuralEvent,
    TrendDirection,
    TrendMaturity,
    TrendState,
)


class TrendEngine:
    """
    Derives directional market state and maturity strictly from validated Structural Events.
    """

    @staticmethod
    def update_trend(
        events: List[StructuralEvent],
        current_state: Optional[TrendState] = None
    ) -> TrendState:
        if current_state is None:
            state = TrendState(
                direction=TrendDirection.SIDEWAYS,
                maturity=TrendMaturity.EMERGING,
                event_count=0,
                bar_age=0,
                confidence=1.0
            )
        else:
            state = current_state

        for event in events:
            # --- BULLISH CONTINUATION ---
            if event.event_type == EventType.BOS_BULLISH:
                if state.direction == TrendDirection.BULLISH:
                    state.event_count += 1
                else:
                    state.direction = TrendDirection.BULLISH
                    state.event_count = 1

            # --- BEARISH CONTINUATION ---
            elif event.event_type == EventType.BOS_BEARISH:
                if state.direction == TrendDirection.BEARISH:
                    state.event_count += 1
                else:
                    state.direction = TrendDirection.BEARISH
                    state.event_count = 1

            # --- BULLISH REVERSAL (CHOCH) ---
            elif event.event_type == EventType.CHOCH_BULLISH:
                state.direction = TrendDirection.BULLISH
                state.event_count = 1

            # --- BEARISH REVERSAL (CHOCH) ---
            elif event.event_type == EventType.CHOCH_BEARISH:
                state.direction = TrendDirection.BEARISH
                state.event_count = 1

            # --- TREND MATURITY EVALUATION ---
            if state.event_count <= 1:
                state.maturity = TrendMaturity.EMERGING
            elif 2 <= state.event_count <= 3:
                state.maturity = TrendMaturity.MATURE
            else:
                state.maturity = TrendMaturity.EXHAUSTED

        return state
