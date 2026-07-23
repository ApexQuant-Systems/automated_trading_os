"""
APEX Quant OS - Market Structure Engine Policy
Centralized configuration, detection thresholds, and engine versioning.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MarketStructurePolicy:
    """
    Immutable configuration policy governing all structural detection algorithms.
    """
    version: str = "3.5.0"
    
    # Extrema Extraction Policy
    extrema_source: Literal["WICKS", "BODIES"] = "WICKS"
    
    # Structural Break Policy
    break_confirmation: Literal["STRICT_BODY", "BALANCED", "AGGRESSIVE_WICK"] = "STRICT_BODY"
    
    # Fractal Swing Detection Parameters
    fractal_left_bars: int = 2
    fractal_right_bars: int = 2
    
    # Inside Bar Handling
    inside_bar_policy: Literal["MERGE", "IGNORE", "COUNT"] = "MERGE"
    
    # Equal Price Tolerance (Percentage)
    equal_price_tolerance_pct: float = 0.0005
    
    # Minimum swing depth required relative to ATR
    atr_filter_multiplier: float = 1.5
