"""
APEX Quant OS - Key Zones Engine (Domain 1: Market Language)
Extracts Fair Value Gaps (FVG) and Institutional Order Blocks (OB).
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from market_language.market_structure.models import Candle, StructuralEvent, EventType


class ZoneType(str, Enum):
    BULLISH_FVG = "BULLISH_FVG"
    BEARISH_FVG = "BEARISH_FVG"
    BULLISH_OB  = "BULLISH_OB"
    BEARISH_OB  = "BEARISH_OB"


@dataclass(frozen=True)
class PriceZone:
    zone_type: ZoneType
    high_price: float
    low_price: float
    creation_timestamp: int
    is_mitigated: bool = False


class KeyZonesEngine:
    """
    Extracts structural supply/demand zones and imbalances.
    """

    @staticmethod
    def detect_fair_value_gaps(candles: List[Candle]) -> List[PriceZone]:
        """
        Detects 3-candle Fair Value Gaps (FVGs).
        """
        fvgs: List[PriceZone] = []
        if len(candles) < 3:
            return fvgs

        for i in range(2, len(candles)):
            c1 = candles[i - 2]
            c3 = candles[i]

            # Bullish FVG: Low of bar 3 is strictly above High of bar 1
            if c3.low > c1.high:
                fvgs.append(
                    PriceZone(
                        zone_type=ZoneType.BULLISH_FVG,
                        high_price=c3.low,
                        low_price=c1.high,
                        creation_timestamp=c3.timestamp
                    )
                )

            # Bearish FVG: High of bar 3 is strictly below Low of bar 1
            elif c3.high < c1.low:
                fvgs.append(
                    PriceZone(
                        zone_type=ZoneType.BEARISH_FVG,
                        high_price=c1.low,
                        low_price=c3.high,
                        creation_timestamp=c3.timestamp
                    )
                )

        return fvgs

    @staticmethod
    def detect_order_blocks(
        candles: List[Candle],
        events: List[StructuralEvent]
    ) -> List[PriceZone]:
        """
        Identifies Order Blocks originating validated structural breakout events.
        """
        order_blocks: List[PriceZone] = []
        if not candles or not events:
            return order_blocks

        ts_to_idx = {c.timestamp: idx for idx, c in enumerate(candles)}

        for evt in events:
            if evt.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_CHOCH_BULLISH]:
                trigger_idx = ts_to_idx.get(evt.trigger_timestamp)
                if trigger_idx is not None and trigger_idx >= 2:
                    for k in range(trigger_idx - 1, -1, -1):
                        c = candles[k]
                        if c.close < c.open:
                            order_blocks.append(
                                PriceZone(
                                    zone_type=ZoneType.BULLISH_OB,
                                    high_price=c.high,
                                    low_price=c.low,
                                    creation_timestamp=c.timestamp
                                )
                            )
                            break

            elif evt.event_type in [EventType.EXTERNAL_BOS_BEARISH, EventType.EXTERNAL_CHOCH_BEARISH]:
                trigger_idx = ts_to_idx.get(evt.trigger_timestamp)
                if trigger_idx is not None and trigger_idx >= 2:
                    for k in range(trigger_idx - 1, -1, -1):
                        c = candles[k]
                        if c.close > c.open:
                            order_blocks.append(
                                PriceZone(
                                    zone_type=ZoneType.BEARISH_OB,
                                    high_price=c.high,
                                    low_price=c.low,
                                    creation_timestamp=c.timestamp
                                )
                            )
                            break

        return order_blocks
