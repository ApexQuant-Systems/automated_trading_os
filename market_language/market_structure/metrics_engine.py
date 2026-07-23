"""
APEX Quant OS - Engine 10: Metrics Engine
Observational, read-only engine providing quantitative analytical statistics.
Strict Rule: Metrics MUST NEVER mutate structural state.
"""

from dataclasses import dataclass
from typing import List
from market_language.market_structure.models import StructuralEvent, StructuralLeg, Swing


@dataclass(frozen=True)
class StructuralMetrics:
    total_swings_detected: int = 0
    total_events_triggered: int = 0
    total_legs_constructed: int = 0
    avg_leg_bar_count: float = 0.0
    avg_leg_price_spread: float = 0.0


class MetricsEngine:
    """
    Computes purely observational, quantitative statistics across structural history.
    """

    @staticmethod
    def compute_metrics(
        swings: List[Swing],
        events: List[StructuralEvent],
        legs: List[StructuralLeg]
    ) -> StructuralMetrics:
        num_swings = len(swings)
        num_events = len(events)
        num_legs = len(legs)

        if num_legs > 0:
            avg_bars = sum(l.bar_count for l in legs) / float(num_legs)
            avg_spread = sum(l.price_range.spread for l in legs) / float(num_legs)
        else:
            avg_bars = 0.0
            avg_spread = 0.0

        return StructuralMetrics(
            total_swings_detected=num_swings,
            total_events_triggered=num_events,
            total_legs_constructed=num_legs,
            avg_leg_bar_count=round(avg_bars, 2),
            avg_leg_price_spread=round(avg_spread, 4)
        )
