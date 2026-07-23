"""
APEX Quant OS - Market Structure Domain Models (v3.1 Frozen Contract)
Level 0 Primitives, Dual-Layer Objects, Events, States, Unique IDs, and Backward Compatibility.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, List


# ============================================================================
# ENUMERATIONS (TYPING & CLASSIFICATION)
# ============================================================================

class HierarchyLevel(str, Enum):
    EXTERNAL = "EXTERNAL"  # Major macro structure (controls trend)
    INTERNAL = "INTERNAL"  # Minor internal structure (pullbacks within leg)
    SUB = "SUB"            # Micro candle-level structure


class SwingOrientation(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class SwingRelationshipType(str, Enum):
    HH = "HH"
    HL = "HL"
    LH = "LH"
    LL = "LL"
    EQH = "EQH"
    EQL = "EQL"
    NONE = "NONE"


class SwingLifecycleState(str, Enum):
    DEVELOPING = "DEVELOPING"
    CONFIRMED = "CONFIRMED"
    PROTECTED_STRONG = "PROTECTED_STRONG"
    WEAK_TARGET = "WEAK_TARGET"
    BROKEN = "BROKEN"
    CONSUMED = "CONSUMED"
    ARCHIVED = "ARCHIVED"


class EventType(str, Enum):
    # External Structural Events
    EXTERNAL_BOS_BULLISH = "EXTERNAL_BOS_BULLISH"
    EXTERNAL_BOS_BEARISH = "EXTERNAL_BOS_BEARISH"
    EXTERNAL_CHOCH_BULLISH = "EXTERNAL_CHOCH_BULLISH"
    EXTERNAL_CHOCH_BEARISH = "EXTERNAL_CHOCH_BEARISH"
    
    # Internal Structural Events
    INTERNAL_BOS_BULLISH = "INTERNAL_BOS_BULLISH"
    INTERNAL_BOS_BEARISH = "INTERNAL_BOS_BEARISH"
    INTERNAL_CHOCH_BULLISH = "INTERNAL_CHOCH_BULLISH"
    INTERNAL_CHOCH_BEARISH = "INTERNAL_CHOCH_BEARISH"
    
    # Liquidity & Inducement Events
    IDM_SWEEP_BULLISH = "IDM_SWEEP_BULLISH"
    IDM_SWEEP_BEARISH = "IDM_SWEEP_BEARISH"
    STRUCTURAL_REJECTION = "STRUCTURAL_REJECTION"


class TrendDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"
    TRANSITION = "TRANSITION"


class TrendMaturity(str, Enum):
    EMERGING = "EMERGING"
    MATURE = "MATURE"
    EXHAUSTED = "EXHAUSTED"


class LegType(str, Enum):
    IMPULSE = "IMPULSE"
    CORRECTION = "CORRECTION"
    EXPANSION = "EXPANSION"
    COMPRESSION = "COMPRESSION"


# ============================================================================
# LEVEL 0: PRIMITIVES
# ============================================================================

@dataclass(frozen=True)
class PricePoint:
    timestamp: int
    price: float


@dataclass(frozen=True)
class PriceRange:
    high: float
    low: float

    @property
    def spread(self) -> float:
        return abs(self.high - self.low)

    @property
    def midpoint(self) -> float:
        return (self.high + self.low) / 2.0


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def body_range(self) -> float:
        return abs(self.close - self.open)

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open


# ============================================================================
# DOMAIN OBJECTS
# ============================================================================

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Swing:
    id: str = field(default_factory=lambda: generate_id("swg"))
    orientation: SwingOrientation = SwingOrientation.HIGH
    price_point: PricePoint = field(default_factory=lambda: PricePoint(0, 0.0))
    hierarchy: HierarchyLevel = HierarchyLevel.INTERNAL
    lifecycle: SwingLifecycleState = SwingLifecycleState.DEVELOPING
    relationship: SwingRelationshipType = SwingRelationshipType.NONE
    candle_index: int = 0
    is_idm: bool = False
    is_strong: bool = False
    caused_displacement: bool = False
    confidence: float = 1.0


@dataclass
class StructuralLeg:
    id: str = field(default_factory=lambda: generate_id("leg"))
    start_swing_id: str = ""
    end_swing_id: str = ""
    hierarchy: HierarchyLevel = HierarchyLevel.EXTERNAL
    direction: TrendDirection = TrendDirection.SIDEWAYS
    leg_type: LegType = LegType.IMPULSE
    price_range: PriceRange = field(default_factory=lambda: PriceRange(0.0, 0.0))
    bar_count: int = 0
    confidence: float = 1.0


@dataclass
class StructuralAnchors:
    protected_high: Optional[Swing] = None
    protected_low: Optional[Swing] = None
    weak_high: Optional[Swing] = None
    weak_low: Optional[Swing] = None
    current_external_high: Optional[Swing] = None
    current_external_low: Optional[Swing] = None
    current_internal_high: Optional[Swing] = None
    current_internal_low: Optional[Swing] = None


@dataclass
class DealingRange:
    high_price: float
    low_price: float
    equilibrium_price: float
    spread: float
    hierarchy: HierarchyLevel = HierarchyLevel.EXTERNAL


@dataclass(frozen=True)
class StructuralEvent:
    id: str = field(default_factory=lambda: generate_id("evt"))
    event_type: EventType = EventType.EXTERNAL_BOS_BULLISH
    trigger_timestamp: int = 0
    trigger_price: float = 0.0
    broken_swing_id: str = ""
    confidence: float = 1.0


@dataclass
class TrendState:
    direction: TrendDirection = TrendDirection.SIDEWAYS
    maturity: TrendMaturity = TrendMaturity.EMERGING
    event_count: int = 0
    bar_age: int = 0
    confidence: float = 1.0


@dataclass(frozen=True)
class EngineMetadata:
    version: str = "3.1.0"
    processed_at_timestamp: int = 0
    processing_time_ms: float = 0.0
    candle_count: int = 0
    symbol: str = "UNKNOWN"
    timeframe: str = "UNKNOWN"
