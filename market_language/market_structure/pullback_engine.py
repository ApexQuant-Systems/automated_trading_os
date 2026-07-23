"""
APEX Quant OS - Engine 8: Pullback Engine
Evaluates validity, depth, and complexity of price retracements within active dealing ranges.
"""

from dataclasses import dataclass
from typing import List, Optional
from market_language.market_structure.models import Candle, DealingRange, StructuralLeg, TrendDirection


@dataclass(frozen=True)
class PullbackStructure:
    is_valid: bool = False
    complexity: str = "NONE"  # NONE, SIMPLE, COMPLEX
    depth_pct: float = 0.0
    in_discount: bool = False
    in_premium: bool = False


class PullbackEngine:
    """
    Analyzes pullback validity and depth relative to the active Dealing Range and Equilibrium.
    """

    @staticmethod
    def evaluate_pullback(
        candles: List[Candle],
        active_leg: Optional[StructuralLeg],
        dealing_range: Optional[DealingRange],
        current_trend: TrendDirection
    ) -> PullbackStructure:
        if not candles or not dealing_range or not active_leg:
            return PullbackStructure()

        latest_candle = candles[-1]
        eq = dealing_range.equilibrium_price
        curr_price = latest_candle.close

        # Calculate depth percentage within the range
        if dealing_range.spread > 0:
            depth_pct = abs(dealing_range.high_price - curr_price) / dealing_range.spread
        else:
            depth_pct = 0.0

        in_discount = curr_price < eq
        in_premium = curr_price > eq

        # Check for Valid Pullback (Price moving against trend)
        is_valid = False
        if current_trend == TrendDirection.BULLISH and curr_price < dealing_range.high_price:
            is_valid = True
        elif current_trend == TrendDirection.BEARISH and curr_price > dealing_range.low_price:
            is_valid = True

        complexity = "SIMPLE" if is_valid and depth_pct < 0.5 else "COMPLEX" if is_valid else "NONE"

        return PullbackStructure(
            is_valid=is_valid,
            complexity=complexity,
            depth_pct=depth_pct,
            in_discount=in_discount,
            in_premium=in_premium
        )
