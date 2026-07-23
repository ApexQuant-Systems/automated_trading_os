"""
APEX Quant OS - Engine 3: Institutional Event Engine (v3.0)
Features: Differentiates External BOS/CHOCH from Internal BOS (MSS) and tracks IDM Sweeps.
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
    Evaluates candle expansion against external and internal swings.
    """

    @classmethod
    def detect_events(
        cls,
        candles: List[Candle],
        external_swings: List[Swing],
        internal_swings: List[Swing],
        current_trend: TrendDirection,
        policy: MarketStructurePolicy
    ) -> Tuple[List[StructuralEvent], List[Swing], List[Swing]]:
        events: List[StructuralEvent] = []
        swept_ids: Set[str] = set()

        all_swings = external_swings + internal_swings

        for idx, candle in enumerate(candles):
            # --- EVALUATE EXTERNAL BREAKS ---
            for s_high in [s for s in external_swings if s.orientation == SwingOrientation.HIGH and s.lifecycle.value in ["CONFIRMED", "PROTECTED_STRONG", "WEAK_TARGET"]]:
                if candle.timestamp <= s_high.price_point.timestamp:
                    continue

                if candle.close > s_high.price_point.price:
                    evt_type = EventType.EXTERNAL_BOS_BULLISH if current_trend == TrendDirection.BULLISH else EventType.EXTERNAL_CHOCH_BULLISH
                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=s_high.id
                        )
                    )
                    s_high.lifecycle = SwingLifecycleState.BROKEN

            for s_low in [s for s in external_swings if s.orientation == SwingOrientation.LOW and s.lifecycle.value in ["CONFIRMED", "PROTECTED_STRONG", "WEAK_TARGET"]]:
                if candle.timestamp <= s_low.price_point.timestamp:
                    continue

                if candle.close < s_low.price_point.price:
                    evt_type = EventType.EXTERNAL_BOS_BEARISH if current_trend == TrendDirection.BEARISH else EventType.EXTERNAL_CHOCH_BEARISH
                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=s_low.id
                        )
                    )
                    s_low.lifecycle = SwingLifecycleState.BROKEN

            # --- EVALUATE INDUCEMENT (IDM) SWEEPS ---
            for idm in [s for s in internal_swings if s.is_idm and s.id not in swept_ids]:
                if candle.timestamp <= idm.price_point.timestamp:
                    continue

                if (idm.orientation == SwingOrientation.LOW and candle.low < idm.price_point.price) or \
                   (idm.orientation == SwingOrientation.HIGH and candle.high > idm.price_point.price):
                    evt_type = EventType.IDM_SWEEP_BULLISH if idm.orientation == SwingOrientation.LOW else EventType.IDM_SWEEP_BEARISH
                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=idm.price_point.price,
                            broken_swing_id=idm.id
                        )
                    )
                    swept_ids.add(idm.id)

        return events, external_swings, internal_swings
