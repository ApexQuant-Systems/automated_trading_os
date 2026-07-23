"""
APEX Quant OS - Engine 5: Leg Engine
Bundles consecutive swings into directional legs and tags them as IMPULSE or CORRECTION.
"""

from typing import List
from market_language.market_structure.models import (
    LegType,
    PriceRange,
    StructuralLeg,
    Swing,
    SwingOrientation,
    TrendDirection,
)


class LegEngine:
    """
    Constructs structural legs connecting opposite swings and classifies their character.
    """

    @staticmethod
    def construct_legs(
        swings: List[Swing],
        current_trend: TrendDirection
    ) -> List[StructuralLeg]:
        """
        Iterates over sorted swings and pairs (Low -> High) or (High -> Low) into StructuralLeg objects.
        """
        if len(swings) < 2:
            return []

        legs: List[StructuralLeg] = []

        for i in range(1, len(swings)):
            prev_s = swings[i - 1]
            curr_s = swings[i]

            # Ensure we are pairing opposite swings (High-Low or Low-High)
            if prev_s.orientation == curr_s.orientation:
                continue

            # Determine Leg Direction
            if prev_s.orientation == SwingOrientation.LOW and curr_s.orientation == SwingOrientation.HIGH:
                leg_dir = TrendDirection.BULLISH
            else:
                leg_dir = TrendDirection.BEARISH

            # Determine Leg Type (Impulse vs Correction)
            if leg_dir == current_trend:
                l_type = LegType.IMPULSE
            else:
                l_type = LegType.CORRECTION

            p_range = PriceRange(
                high=max(prev_s.price_point.price, curr_s.price_point.price),
                low=min(prev_s.price_point.price, curr_s.price_point.price)
            )

            bar_cnt = abs(curr_s.candle_index - prev_s.candle_index)

            legs.append(
                StructuralLeg(
                    start_swing_id=prev_s.id,
                    end_swing_id=curr_s.id,
                    direction=leg_dir,
                    leg_type=l_type,
                    price_range=p_range,
                    bar_count=bar_cnt,
                    confidence=min(prev_s.confidence, curr_s.confidence)
                )
            )

        return legs
