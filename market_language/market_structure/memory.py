"""
APEX Quant OS - Persistent Structure Memory
State repository enabling replay, historical lookups, and cross-engine queries.
"""

from typing import Dict, List, Optional
from market_language.market_structure.models import (
    DealingRange,
    StructuralAnchors,
    StructuralEvent,
    StructuralLeg,
    Swing,
    TrendState,
)


class StructureMemory:
    """
    Read-write persistent store for confirmed historical and active structure.
    Used for candle-by-candle state updates and historical replay queries.
    """

    def __init__(self):
        self.swings: List[Swing] = []
        self._swing_index: Dict[str, Swing] = {}
        self.legs: List[StructuralLeg] = []
        self.events: List[StructuralEvent] = []
        self.trend_history: List[TrendState] = []
        self.anchor_history: List[StructuralAnchors] = []
        self.boundary_history: List[DealingRange] = []

    def add_swing(self, swing: Swing) -> None:
        if swing.id not in self._swing_index:
            self.swings.append(swing)
            self._swing_index[swing.id] = swing

    def get_swing_by_id(self, swing_id: str) -> Optional[Swing]:
        return self._swing_index.get(swing_id)

    def add_event(self, event: StructuralEvent) -> None:
        self.events.append(event)

    def add_leg(self, leg: StructuralLeg) -> None:
        self.legs.append(leg)

    def update_trend(self, trend: TrendState) -> None:
        self.trend_history.append(trend)

    def update_anchors(self, anchors: StructuralAnchors) -> None:
        self.anchor_history.append(anchors)

    def update_boundary(self, boundary: DealingRange) -> None:
        self.boundary_history.append(boundary)

    def get_active_swings(self) -> List[Swing]:
        return [s for s in self.swings if s.lifecycle.value in ["CONFIRMED", "PROTECTED", "WEAK"]]

    def clear(self) -> None:
        self.swings.clear()
        self._swing_index.clear()
        self.legs.clear()
        self.events.clear()
        self.trend_history.clear()
        self.anchor_history.clear()
        self.boundary_history.clear()
