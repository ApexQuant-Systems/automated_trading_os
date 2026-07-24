"""
APEX Quant OS - Key Levels Engine (Domain 1: Market Language)
Detects Equal Highs/Lows (EQH/EQL) and Previous Day High/Low (PDH/PDL).
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from market_language.market_structure.models import Candle, Swing, SwingOrientation


class LevelType(str, Enum):
    EQH = "EQH"        # Equal Highs (Buy-side Liquidity Pool)
    EQL = "EQL"        # Equal Lows (Sell-side Liquidity Pool)
    PDH = "PDH"        # Previous Day High
    PDL = "PDL"        # Previous Day Low


@dataclass(frozen=True)
class KeyLevel:
    level_type: LevelType
    price: float
    timestamp: int
    is_swept: bool = False


class KeyLevelsEngine:
    """
    Extracts structural price levels acting as liquidity pools.
    """

    @staticmethod
    def detect_equal_levels(
        swings: List[Swing],
        tolerance_pct: float = 0.0005
    ) -> List[KeyLevel]:
        """
        Identifies Equal Highs (EQH) and Equal Lows (EQL) within a given percentage tolerance.
        """
        key_levels: List[KeyLevel] = []
        highs = [s for s in swings if s.orientation == SwingOrientation.HIGH]
        lows = [s for s in swings if s.orientation == SwingOrientation.LOW]

        # Evaluate Equal Highs
        for i in range(len(highs) - 1):
            h1 = highs[i].price_point.price
            h2 = highs[i + 1].price_point.price
            if abs(h1 - h2) / h1 <= tolerance_pct:
                key_levels.append(
                    KeyLevel(
                        level_type=LevelType.EQH,
                        price=(h1 + h2) / 2.0,
                        timestamp=highs[i + 1].price_point.timestamp
                    )
                )

        # Evaluate Equal Lows
        for i in range(len(lows) - 1):
            l1 = lows[i].price_point.price
            l2 = lows[i + 1].price_point.price
            if abs(l1 - l2) / l1 <= tolerance_pct:
                key_levels.append(
                    KeyLevel(
                        level_type=LevelType.EQL,
                        price=(l1 + l2) / 2.0,
                        timestamp=lows[i + 1].price_point.timestamp
                    )
                )

        return key_levels

    @staticmethod
    def detect_htf_levels(candles: List[Candle]) -> List[KeyLevel]:
        """
        Identifies Previous Day High (PDH) and Previous Day Low (PDL) based on UTC calendar days.
        """
        if not candles:
            return []

        # Group candles by UTC calendar date
        daily_candles = {}
        for c in candles:
            dt = datetime.fromtimestamp(c.timestamp / 1000, tz=timezone.utc)
            day_key = dt.strftime("%Y-%m-%d")
            if day_key not in daily_candles:
                daily_candles[day_key] = []
            daily_candles[day_key].append(c)

        days = sorted(daily_candles.keys())
        if len(days) < 2:
            return []

        prev_day = days[-2]
        prev_day_bars = daily_candles[prev_day]

        pdh = max(c.high for c in prev_day_bars)
        pdl = min(c.low for c in prev_day_bars)
        ts = prev_day_bars[-1].timestamp

        return [
            KeyLevel(level_type=LevelType.PDH, price=pdh, timestamp=ts),
            KeyLevel(level_type=LevelType.PDL, price=pdl, timestamp=ts)
        ]
