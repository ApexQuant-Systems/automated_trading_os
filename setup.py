import os

os.makedirs('configs', exist_ok=True)
os.makedirs('market_language', exist_ok=True)
os.makedirs('tests', exist_ok=True)

sets_code = """from dataclasses import dataclass
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
"""

engine_code = """from dataclasses import dataclass
from typing import Any, List, Tuple

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.key_levels import KeyLevelsEngine, KeyLevel
from market_language.key_zones import KeyZonesEngine, PriceZone
from market_language.market_structure.phase_engine import MarketPhase, PhaseEngine

@dataclass(frozen=True)
class TimeframeState:
    timeframe: str
    last_timestamp: int
    last_close: float
    trend_direction: str
    internal_swings: Tuple[Any, ...]
    external_swings: Tuple[Any, ...]
    recent_events: Tuple[Any, ...]
    protected_low: Any
    protected_high: Any
    equal_levels: Tuple[KeyLevel, ...]
    fair_value_gaps: Tuple[PriceZone, ...]
    order_blocks: Tuple[PriceZone, ...]
    phase: MarketPhase
    is_premium: bool
    is_discount: bool

class TimeframeEngine:
    def __init__(self, policy: Any = None):
        self.policy = policy or MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
        self.structure_compiler = StructureCompiler(policy=self.policy)

    def evaluate(self, candles: List[Candle], timeframe: str = "1H") -> TimeframeState:
        if not candles:
            raise ValueError("Cannot evaluate empty candle list.")
        last_candle = candles[-1]
        struct_state = self.structure_compiler.compile(candles, symbol="ASSET", timeframe=timeframe)
        equal_levels = tuple(KeyLevelsEngine.detect_equal_levels(list(struct_state.internal_swings)))
        fvgs = tuple(KeyZonesEngine.detect_fair_value_gaps(candles))
        obs = tuple(KeyZonesEngine.detect_order_blocks(candles, list(struct_state.recent_events)))
        current_phase = PhaseEngine.classify_phase(
            events=list(struct_state.recent_events),
            trend=struct_state.trend,
            anchors=struct_state.anchors,
            latest_price=last_candle.close
        )
        is_premium = False
        is_discount = False
        if struct_state.dealing_range:
            is_premium = last_candle.close > struct_state.dealing_range.equilibrium_price
            is_discount = last_candle.close < struct_state.dealing_range.equilibrium_price

        return TimeframeState(
            timeframe=timeframe,
            last_timestamp=last_candle.timestamp,
            last_close=last_candle.close,
            trend_direction=struct_state.trend.direction.value,
            internal_swings=tuple(struct_state.internal_swings),
            external_swings=tuple(struct_state.external_swings),
            recent_events=tuple(struct_state.recent_events),
            protected_low=struct_state.anchors.protected_low,
            protected_high=struct_state.anchors.protected_high,
            equal_levels=equal_levels,
            fair_value_gaps=fvgs,
            order_blocks=obs,
            phase=current_phase,
            is_premium=is_premium,
            is_discount=is_discount
        )
"""

test_code = """import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle
from market_language.timeframe_engine import TimeframeEngine

def test_timeframe_engine_evaluation():
    print("Executing tests/test_timeframe_engine.py...")
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 100.5, 100),
        Candle(2000, 100.5, 101.0, 97.0, 97.5, 100),
        Candle(3000, 97.5, 110.0, 97.0, 109.0, 300),
        Candle(4000, 109.0, 120.0, 105.0, 118.0, 300),
        Candle(5000, 118.0, 117.0, 108.0, 109.0, 100),
        Candle(6000, 109.0, 125.0, 108.0, 124.0, 300),
        Candle(7000, 124.0, 123.0, 115.0, 116.0, 100),
    ]
    engine = TimeframeEngine()
    tf_state = engine.evaluate(candles, timeframe="4H")

    assert tf_state.timeframe == "4H"
    assert tf_state.last_close == 116.0
    assert tf_state.trend_direction == "BULLISH"
    assert len(tf_state.fair_value_gaps) >= 1
    assert tf_state.phase is not None

    print("\\n--- 4H TIMEFRAME STATE SNAPSHOT VERIFIED ---")
    print(f" Timeframe: {tf_state.timeframe}")
    print(f" Last Close: ${tf_state.last_close:.2f}")
    print(f" Trend Direction: {tf_state.trend_direction}")
    print(f" Market Phase: {tf_state.phase.value}")
    print(f" Fair Value Gaps: {len(tf_state.fair_value_gaps)}")
    print("--------------------------------------------")
    print("  ✅ PASS: test_timeframe_engine_evaluation Passed!")

if __name__ == "__main__":
    test_timeframe_engine_evaluation()
"""

with open('configs/sets.py', 'w') as f:
    f.write(sets_code)

with open('market_language/timeframe_engine.py', 'w') as f:
    f.write(engine_code)

with open('tests/test_timeframe_engine.py', 'w') as f:
    f.write(test_code)

print("  ✅ SUCCESS: All 3 files generated cleanly!")
