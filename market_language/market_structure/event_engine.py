"""
APEX Quant OS - Engine 3: Institutional Event Engine (v3.5.3)
Features: True BOS Validation (Displacement + Imbalance / FVG) AND Debounced Wick Sweep (STRUCTURAL_REJECTION) Detection.
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
    Evaluates institutional expansion against external/internal swings.
    Enforces body displacement, ATR expansion, FVG imbalance for BOS,
    and debounced wick sweeps for STRUCTURAL_REJECTION events.
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
        external_swings: List[Swing],
        internal_swings: List[Swing],
        current_trend: TrendDirection,
        policy: MarketStructurePolicy
    ) -> Tuple[List[StructuralEvent], List[Swing], List[Swing]]:
        events: List[StructuralEvent] = []
        swept_ids: Set[str] = set()

        for idx, candle in enumerate(candles):
            atr = cls._calculate_atr_simple(candles, idx)
            disp_ratio = candle.body_range / candle.range if candle.range > 0 else 0.0
            is_expansion_candle = candle.range >= (1.0 * atr)

            # Check for 3-bar Fair Value Imbalance (FVG)
            has_bullish_fvg = False
            has_bearish_fvg = False
            if idx >= 2:
                c1 = candles[idx - 2]
                c3 = candle
                if c3.low > c1.high:
                    has_bullish_fvg = True
                if c3.high < c1.low:
                    has_bearish_fvg = True

            # --- 1. EVALUATE EXTERNAL HIGHS ---
            for s_high in [s for s in external_swings if s.orientation == SwingOrientation.HIGH and s.lifecycle.value in ["DEVELOPING", "CONFIRMED", "PROTECTED_STRONG", "WEAK_TARGET"]]:
                if candle.timestamp <= s_high.price_point.timestamp:
                    continue

                level = s_high.price_point.price

                # A. True Bullish BOS (Body Close > Level + Displacement/FVG)
                if candle.close > level and disp_ratio >= 0.45 and (is_expansion_candle or has_bullish_fvg):
                    evt_type = EventType.EXTERNAL_BOS_BULLISH if current_trend == TrendDirection.BULLISH else EventType.EXTERNAL_CHOCH_BULLISH
                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=s_high.id,
                            confidence=s_high.confidence
                        )
                    )
                    s_high.lifecycle = SwingLifecycleState.BROKEN

                # B. Wick Sweep (Structural Rejection) — High > Level, Close <= Level
                elif candle.high > level and candle.close <= level:
                    if s_high.id not in swept_ids:
                        events.append(
                            StructuralEvent(
                                event_type=EventType.STRUCTURAL_REJECTION,
                                trigger_timestamp=candle.timestamp,
                                trigger_price=candle.high,
                                broken_swing_id=s_high.id,
                                confidence=0.8
                            )
                        )
                        swept_ids.add(s_high.id)

            # --- 2. EVALUATE EXTERNAL LOWS ---
            for s_low in [s for s in external_swings if s.orientation == SwingOrientation.LOW and s.lifecycle.value in ["DEVELOPING", "CONFIRMED", "PROTECTED_STRONG", "WEAK_TARGET"]]:
                if candle.timestamp <= s_low.price_point.timestamp:
                    continue

                level = s_low.price_point.price

                # A. True Bearish BOS
                if candle.close < level and disp_ratio >= 0.45 and (is_expansion_candle or has_bearish_fvg):
                    evt_type = EventType.EXTERNAL_BOS_BEARISH if current_trend == TrendDirection.BEARISH else EventType.EXTERNAL_CHOCH_BEARISH
                    events.append(
                        StructuralEvent(
                            event_type=evt_type,
                            trigger_timestamp=candle.timestamp,
                            trigger_price=candle.close,
                            broken_swing_id=s_low.id,
                            confidence=s_low.confidence
                        )
                    )
                    s_low.lifecycle = SwingLifecycleState.BROKEN

                # B. Wick Sweep (Structural Rejection) — Low < Level, Close >= Level
                elif candle.low < level and candle.close >= level:
                    if s_low.id not in swept_ids:
                        events.append(
                            StructuralEvent(
                                event_type=EventType.STRUCTURAL_REJECTION,
                                trigger_timestamp=candle.timestamp,
                                trigger_price=candle.low,
                                broken_swing_id=s_low.id,
                                confidence=0.8
                            )
                        )
                        swept_ids.add(s_low.id)

            # --- 3. EVALUATE INDUCEMENT (IDM) SWEEPS ---
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
                            broken_swing_id=idm.id,
                            confidence=0.9
                        )
                    )
                    swept_ids.add(idm.id)

        return events, external_swings, internal_swings
