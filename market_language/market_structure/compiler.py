"""
APEX Quant OS - Engine 12: Structure Compiler (v3.0 Dual-Layer)
Executes dual-layer internal/external structure pipeline and outputs MarketStructureState.
"""

import time
from dataclasses import dataclass
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
    metadata: EngineMetadata
    trend: TrendState
    anchors: StructuralAnchors
    dealing_range: Optional[DealingRange]
    active_leg: Optional[StructuralLeg]
    pullback: PullbackStructure
    quality: StructuralQuality
    metrics: StructuralMetrics
    recent_events: Tuple[StructuralEvent, ...]
    external_swings: Tuple[Swing, ...]
    internal_swings: Tuple[Swing, ...]


class StructureCompiler:
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

        # Engine 1: Detect External & Internal Swings
        external_swings, internal_swings = SwingEngine.detect_swings(candles, self.policy)

        # Engine 2: Relationships
        external_swings = RelationshipEngine.evaluate_relationships(external_swings, self.policy)

        # Retrieve Trend
        current_trend = self.memory.trend_history[-1].direction if self.memory.trend_history else TrendState().direction

        # Engine 3: Events
        events, external_swings, internal_swings = EventEngine.detect_events(
            candles, external_swings, internal_swings, current_trend, self.policy
        )

        # Engine 4: Trend
        trend = TrendEngine.update_trend(events, self.memory.trend_history[-1] if self.memory.trend_history else None)

        # Engine 5: Legs
        legs = LegEngine.construct_legs(external_swings, trend.direction)

        # Engine 6: Anchors
        anchors = AnchorEngine.derive_anchors(external_swings, events, trend.direction)

        # Engine 7: Dealing Range
        dealing_range = BoundaryEngine.compute_dealing_range(anchors)

        # Engine 8: Pullback
        active_leg = legs[-1] if legs else None
        pullback = PullbackEngine.evaluate_pullback(candles, active_leg, dealing_range, trend.direction)

        # Engine 9: Quality
        quality = QualityEngine.evaluate_quality(candles, legs)

        # Engine 10: Metrics
        metrics = MetricsEngine.compute_metrics(external_swings, events, legs)

        # Engine 11: Validate
        is_valid, validation_errors = StructureValidator.validate_state(trend, anchors, dealing_range)
        if not is_valid:
            raise ValueError(f"MarketStructureState validation failed: {validation_errors}")

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0

        metadata = EngineMetadata(
            version="3.0.0",
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
            external_swings=tuple(external_swings),
            internal_swings=tuple(internal_swings)
        )
