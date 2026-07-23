"""
APEX Quant OS - Engine 4: Institutional Trend Engine (v3.0 Dual-Layer)
Updates TrendState based on External and Internal Structural Events.
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
            if event.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.INTERNAL_BOS_BULLISH]:
                if state.direction == TrendDirection.BULLISH:
                    state.event_count += 1
                else:
                    state.direction = TrendDirection.BULLISH
                    state.event_count = 1

            # --- BEARISH CONTINUATION ---
            elif event.event_type in [EventType.EXTERNAL_BOS_BEARISH, EventType.INTERNAL_BOS_BEARISH]:
                if state.direction == TrendDirection.BEARISH:
                    state.event_count += 1
                else:
                    state.direction = TrendDirection.BEARISH
                    state.event_count = 1

            # --- BULLISH REVERSAL (CHOCH) ---
            elif event.event_type in [EventType.EXTERNAL_CHOCH_BULLISH, EventType.INTERNAL_CHOCH_BULLISH]:
                state.direction = TrendDirection.BULLISH
                state.event_count = 1

            # --- BEARISH REVERSAL (CHOCH) ---
            elif event.event_type in [EventType.EXTERNAL_CHOCH_BEARISH, EventType.INTERNAL_CHOCH_BEARISH]:
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
