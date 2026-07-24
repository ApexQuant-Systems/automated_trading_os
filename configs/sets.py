from dataclasses import dataclass
from enum import Enum

class TimeframeSetID(str, Enum):
    SET_1_INVESTING = "SET_1_INVESTING"
    SET_2_POSITIONAL = "SET_2_POSITIONAL"
    SET_3_SWING = "SET_3_SWING"
    SET_4_INTRADAY = "SET_4_INTRADAY"

@dataclass(frozen=True)
class TimeframeSetConfig:
    set_id: TimeframeSetID
    htf: str
    mtf: str
    ltf: str

TIMEFRAME_SETS = {
    TimeframeSetID.SET_1_INVESTING: TimeframeSetConfig(TimeframeSetID.SET_1_INVESTING, "1M", "1W", "1D"),
    TimeframeSetID.SET_2_POSITIONAL: TimeframeSetConfig(TimeframeSetID.SET_2_POSITIONAL, "1W", "1D", "4H"),
    TimeframeSetID.SET_3_SWING: TimeframeSetConfig(TimeframeSetID.SET_3_SWING, "1D", "4H", "1H"),
    TimeframeSetID.SET_4_INTRADAY: TimeframeSetConfig(TimeframeSetID.SET_4_INTRADAY, "4H", "1H", "15M"),
}
