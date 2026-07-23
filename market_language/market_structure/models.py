"""
APEX Quant OS - Market Structure Domain Models
Level 0 Primitives, Persistent Objects, Point-in-Time Events, and Evaluative States.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


# ============================================================================
# ENUMERATIONS (TYPING & CLASSIFICATION)
# ============================================================================

class HierarchyLevel(str, Enum):
    EXTERNAL = "EXTERNAL"  # Major macro structure
    INTERNAL = "INTERNAL"  # Minor structure (pullback leg)
    SUB = "SUB"            # Micro sub-structure (candle-level)


class SwingOrientation(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class SwingRelationshipType(str, Enum):
    HH = "HH"  # Higher High
    HL = "HL"  # Higher Low
    LH = "LH"  # Lower High
    LL = "LL"  # Lower Low
    EQH = "EQH"  # Equal High
    EQL = "EQL"  # Equal Low
    NONE = "NONE"


class SwingLifecycleState(str, Enum):
    DEVELOPING = "DEVELOPING"
    CONFIRMED = "CONFIRMED"
    PROTECTED = "PROTECTED"
    WEAK = "WEAK"
    BROKEN = "BROKEN"
    CONSUMED = "CONSUMED"
    ARCHIVED = "ARCHIVED"


class EventType(str, Enum):
    BOS_BULLISH = "BOS_BULLISH"
    BOS_BEARISH = "BOS_BEARISH"
    CHOCH_BULLISH = "CHOCH_BULLISH"
    CHOCH_BEARISH = "CHOCH_BEARISH"
    MSS_BULLISH = "MSS_BULLISH"
    MSS_BEARISH = "MSS_BEARISH"
    SMS = "SMS"  # Shift in Market Structure / Failure Swing
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
# LEVEL 0: PRIMITIVE TYPES
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
# OBJECTS (PERSISTENT PHYSICAL STRUCTURES)
# ============================================================================

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@dataclass
class Swing:
    id: str = field(default_factory=lambda: generate_id("swg"))
    orientation: SwingOrientation = SwingOrientation.HIGH
    price_point: PricePoint = field(default_factory=lambda: PricePoint(0, 0.0))
    hierarchy: HierarchyLevel = HierarchyLevel.EXTERNAL
    lifecycle: SwingLifecycleState = SwingLifecycleState.DEVELOPING
    relationship: SwingRelationshipType = SwingRelationshipType.NONE
    candle_index: int = 0
    confidence: float = 1.0


@dataclass
class StructuralLeg:
    id: str = field(default_factory=lambda: generate_id("leg"))
    start_swing_id: str = ""
    end_swing_id: str = ""
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


@dataclass
class DealingRange:
    high_price: float
    low_price: float
    equilibrium_price: float
    spread: float


# ============================================================================
# EVENTS (POINT-IN-TIME STRUCTURAL BREAKS)
# ============================================================================

@dataclass(frozen=True)
class StructuralEvent:
    id: str = field(default_factory=lambda: generate_id("evt"))
    event_type: EventType = EventType.BOS_BULLISH
    trigger_timestamp: int = 0
    trigger_price: float = 0.0
    broken_swing_id: str = ""
    confidence: float = 1.0


# ============================================================================
# STATES (EVALUATIVE CONDITION FLAGS)
# ============================================================================

@dataclass
class TrendState:
    direction: TrendDirection = TrendDirection.SIDEWAYS
    maturity: TrendMaturity = TrendMaturity.EMERGING
    event_count: int = 0
    bar_age: int = 0
    confidence: float = 1.0


@dataclass(frozen=True)
class EngineMetadata:
    version: str = "2.0.0"
    processed_at_timestamp: int = 0
    processing_time_ms: float = 0.0
    candle_count: int = 0
    symbol: str = "UNKNOWN"
    timeframe: str = "UNKNOWN"
