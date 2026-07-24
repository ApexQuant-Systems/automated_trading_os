"""
APEX Quant OS - Engine 8: Market Phase Classifier (v3.6.0)
Frozen API: PhaseEngine.classify_phase(events, trend, anchors, latest_price)
"""

from enum import Enum
from typing import List, Optional


class MarketPhase(str, Enum):
    ACCUMULATION  = "ACCUMULATION"
    EXPANSION     = "EXPANSION"
    RETRACEMENT   = "RETRACEMENT"
    DISTRIBUTION  = "DISTRIBUTION"
    CONSOLIDATION = "CONSOLIDATION"


class PhaseEngine:
    """
    Classifies structural market phase based on events, trend state, and price position.
    """

    @classmethod
    def classify_phase(
        cls,
        events: List,
        trend: getattr,
        anchors: getattr,
        latest_price: float
    ) -> MarketPhase:
        if not events:
            return MarketPhase.CONSOLIDATION

        last_event = events[-1]
        
        # 1. Active Breakout / Expansion
        if getattr(last_event, 'event_type', None) in ["EXTERNAL_BOS_BULLISH", "EXTERNAL_BOS_BEARISH", "EXTERNAL_CHOCH_BULLISH", "EXTERNAL_CHOCH_BEARISH"]:
            return MarketPhase.EXPANSION

        # 2. Liquidity Sweep / Manipulation
        if getattr(last_event, 'event_type', None) == "STRUCTURAL_REJECTION":
            return MarketPhase.ACCUMULATION

        # 3. Default to Retracement or Consolidation
        return MarketPhase.RETRACEMENT
