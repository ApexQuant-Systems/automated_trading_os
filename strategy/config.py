"""
APEX Quant OS - Domain 2: Strategy Configuration & Timeframe Sets
Configures fractal multi-timeframe sets for trading styles.
"""

from dataclasses import dataclass
from enum import Enum


class TimeframeSetID(str, Enum):
    SET_1_INVESTING  = "SET_1_INVESTING"   # 1M -> 1W -> 1D
    SET_2_POSITIONAL = "SET_2_POSITIONAL"  # 1W -> 1D -> 4H
    SET_3_SWING      = "SET_3_SWING"       # 1D -> 4H -> 1H
    SET_4_INTRADAY   = "SET_4_INTRADAY"    # 4H -> 1H -> 15M


@dataclass(frozen=True)
class TimeframeSetConfig:
    set_id: TimeframeSetID
    htf: str  # High Timeframe (Bias)
    mtf: str  # Medium Timeframe (Setup / Alignment)
    ltf: str  # Low Timeframe (Entry)


# Pre-configured Timeframe Sets
TIMEFRAME_SETS = {
    TimeframeSetID.SET_1_INVESTING:  TimeframeSetConfig(TimeframeSetID.SET_1_INVESTING,  htf="1M", mtf="1W", ltf="1D"),
    TimeframeSetID.SET_2_POSITIONAL: TimeframeSetConfig(TimeframeSetID.SET_2_POSITIONAL, htf="1W", mtf="1D", ltf="4H"),
    TimeframeSetID.SET_3_SWING:      TimeframeSetConfig(TimeframeSetID.SET_3_SWING,      htf="1D", mtf="4H", ltf="1H"),
    TimeframeSetID.SET_4_INTRADAY:   TimeframeSetConfig(TimeframeSetID.SET_4_INTRADAY,   htf="4H", mtf="1H", ltf="15M"),
}
