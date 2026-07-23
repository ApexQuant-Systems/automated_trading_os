"""
APEX Quant OS - Engine 9: Quality Engine
Calculates structural clarity, choppiness, and displacement efficiency.
"""

from dataclasses import dataclass
from typing import List
from market_language.market_structure.models import Candle, StructuralLeg


@dataclass(frozen=True)
class StructuralQuality:
    quality_score: float = 1.0  # 0.0 (Extreme Noise/Chop) to 1.0 (Clean Trend)
    classification: str = "CLEAN"  # CLEAN, CHOPPY, OVERLAPPING


class QualityEngine:
    """
    Assesses market structure clarity by evaluating displacement vs candle overlap.
    """

    @staticmethod
    def evaluate_quality(
        candles: List[Candle],
        legs: List[StructuralLeg]
    ) -> StructuralQuality:
        if len(candles) < 5:
            return StructuralQuality(quality_score=1.0, classification="CLEAN")

        # Calculate efficiency ratio: Net displacement / Total distance traveled
        net_move = abs(candles[-1].close - candles[0].open)
        total_path = sum(c.range for c in candles)

        if total_path == 0:
            efficiency = 1.0
        else:
            efficiency = min(1.0, max(0.0, net_move / total_path))

        if efficiency >= 0.4:
            classification = "CLEAN"
        elif efficiency >= 0.2:
            classification = "OVERLAPPING"
        else:
            classification = "CHOPPY"

        return StructuralQuality(
            quality_score=round(efficiency, 4),
            classification=classification
        )
