"""
APEX Quant OS - Engine 12: Structure Compiler
Master Orchestrator. Executes Pipeline (Engines 1-11), updates Memory, and outputs MarketStructureState.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from market_language.market_structure.anchor_engine import AnchorEngine
from market_language.market_structure.boundary_engine import BoundaryEngine
from market_language.market_structure.event_engine import EventEngine
from market_language.market_structure.leg_engine import LegEngine
from market_language.market_structure.memory import StructureMemory
from market_language.market_structure.metrics_engine import MetricsEngine, StructuralMetrics
from market_language.market_structure.models import (
    Candle,
    DealingRange,
    EngineMetadata,
    HierarchyLevel,
    StructuralAnchors,
    StructuralEvent,
    StructuralLeg,
    Swing,
    TrendState,
)
from market_language.market_structure.policy import MarketStructurePolicy
from market_language.market_structure.pullback_engine import PullbackEngine, PullbackStructure
from market_language.market_structure.quality_engine import QualityEngine, StructuralQuality
from market_language.market_structure.relationship_engine import RelationshipEngine
from market_language.market_structure.swing_engine import SwingEngine
from market_language.market_structure.trend_engine import TrendEngine
from market_language.market_structure.validator import StructureValidator


@dataclass(frozen=True)
class MarketStructureState:
    """
    Immutable consolidated snapshot of Market Structure at a specific point in time.
    """
    metadata: EngineMetadata
    trend: TrendState
    anchors: StructuralAnchors
    dealing_range: Optional[DealingRange]
    active_leg: Optional[StructuralLeg]
    pullback: PullbackStructure
    quality: StructuralQuality
    metrics: StructuralMetrics
    recent_events: Tuple[StructuralEvent, ...]
    active_swings: Tuple[Swing, ...]


class StructureCompiler:
    """
    Master orchestrator for the Market Structure Engine.
    Executes all sub-engines deterministically and returns validated MarketStructureState.
    """

    def __init__(self, policy: Optional[MarketStructurePolicy] = None):
        self.policy = policy if policy is not None else MarketStructurePolicy()
        self.memory = StructureMemory()

    def compile(
        self,
        candles: List[Candle],
        symbol: str = "BTCUSDT",
        timeframe: str = "1H"
    ) -> MarketStructureState:
        start_time = time.perf_counter()

        # Engine 1: Detect Swings
        swings = SwingEngine.detect_swings(candles, self.policy, HierarchyLevel.EXTERNAL)

        # Engine 2: Evaluate Relationships (HH, HL, LH, LL)
        swings = RelationshipEngine.evaluate_relationships(swings, self.policy)

        # Retrieve current trend direction for event classification
        current_trend = self.memory.trend_history[-1].direction if self.memory.trend_history else TrendState().direction

        # Engine 3: Detect Structural Events (BOS, CHOCH, MSS)
        events, updated_swings = EventEngine.detect_events(candles, swings, current_trend, self.policy)

        # Engine 4: Update Trend State
        trend = TrendEngine.update_trend(events, self.memory.trend_history[-1] if self.memory.trend_history else None)

        # Engine 5: Construct Structural Legs
        legs = LegEngine.construct_legs(updated_swings, trend.direction)

        # Engine 6: Derive Anchors
        anchors = AnchorEngine.derive_anchors(updated_swings, events, trend.direction)

        # Engine 7: Compute Dealing Range & Boundaries
        dealing_range = BoundaryEngine.compute_dealing_range(anchors)

        # Engine 8: Evaluate Pullback Structure
        active_leg = legs[-1] if legs else None
        pullback = PullbackEngine.evaluate_pullback(candles, active_leg, dealing_range, trend.direction)

        # Engine 9: Assess Quality
        quality = QualityEngine.evaluate_quality(candles, legs)

        # Engine 10: Compute Quantitative Metrics
        metrics = MetricsEngine.compute_metrics(updated_swings, events, legs)

        # Engine 11: Validate State via Firewall
        is_valid, validation_errors = StructureValidator.validate_state(trend, anchors, dealing_range)
        if not is_valid:
            raise ValueError(f"MarketStructureState validation failed: {validation_errors}")

        # Update Memory
        for s in updated_swings:
            self.memory.add_swing(s)
        for e in events:
            self.memory.add_event(e)
        for l in legs:
            self.memory.add_leg(l)
        self.memory.update_trend(trend)
        self.memory.update_anchors(anchors)
        if dealing_range:
            self.memory.update_boundary(dealing_range)

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0

        metadata = EngineMetadata(
            version=self.policy.version,
            processed_at_timestamp=candles[-1].timestamp if candles else 0,
            processing_time_ms=round(execution_time_ms, 2),
            candle_count=len(candles),
            symbol=symbol,
            timeframe=timeframe
        )

        return MarketStructureState(
            metadata=metadata,
            trend=trend,
            anchors=anchors,
            dealing_range=dealing_range,
            active_leg=active_leg,
            pullback=pullback,
            quality=quality,
            metrics=metrics,
            recent_events=tuple(events),
            active_swings=tuple(updated_swings)
        )
