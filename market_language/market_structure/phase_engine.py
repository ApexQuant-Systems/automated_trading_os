"""
APEX Quant OS - Engine 13: Market Phase Classifier (v3.2)
Classifies the active structural environment into institutional market phases:
EXPANSION, MANIPULATION, RETRACEMENT, or CONSOLIDATION.
"""

from enum import Enum
from typing import List, Optional
from market_language.market_structure.models import (
    DealingRange,
    EventType,
    StructuralEvent,
    StructuralLeg,
    TrendDirection,
)


class MarketPhase(str, Enum):
    EXPANSION = "EXPANSION"        # Active displacement leg breaking structure
    MANIPULATION = "MANIPULATION"  # IDM sweep or liquidity raid active
    RETRACEMENT = "RETRACEMENT"    # Price pulling back into Premium/Discount
    CONSOLIDATION = "CONSOLIDATION" # Price compressing inside equilibrium


class PhaseEngine:
    """
    Evaluates recent structural events and active leg character to assign MarketPhase.
    """

    @staticmethod
    def classify_phase(
        events: List[StructuralEvent],
        active_leg: Optional[StructuralLeg],
        dealing_range: Optional[DealingRange],
        latest_price: float
    ) -> MarketPhase:
        if not events:
            return MarketPhase.CONSOLIDATION

        latest_event = events[-1]

        # 1. MANIPULATION: Recent IDM sweep or Structural Rejection
        if latest_event.event_type in [EventType.IDM_SWEEP_BULLISH, EventType.IDM_SWEEP_BEARISH, EventType.STRUCTURAL_REJECTION]:
            return MarketPhase.MANIPULATION

        # 2. EXPANSION: Recent External BOS or CHOCH
        if latest_event.event_type in [
            EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_BOS_BEARISH,
            EventType.EXTERNAL_CHOCH_BULLISH, EventType.EXTERNAL_CHOCH_BEARISH
        ]:
            return MarketPhase.EXPANSION

        # 3. RETRACEMENT / CONSOLIDATION: Evaluate position inside dealing range
        if dealing_range and active_leg:
            eq = dealing_range.equilibrium_price
            if active_leg.direction == TrendDirection.BULLISH and latest_price < eq:
                return MarketPhase.RETRACEMENT
            elif active_leg.direction == TrendDirection.BEARISH and latest_price > eq:
                return MarketPhase.RETRACEMENT

        return MarketPhase.CONSOLIDATION
