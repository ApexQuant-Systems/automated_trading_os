import os
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

    print("\n--- 4H TIMEFRAME STATE SNAPSHOT VERIFIED ---")
    print(f" Timeframe: {tf_state.timeframe}")
    print(f" Last Close: ${tf_state.last_close:.2f}")
    print(f" Trend Direction: {tf_state.trend_direction}")
    print(f" Market Phase: {tf_state.phase.value}")
    print(f" Fair Value Gaps: {len(tf_state.fair_value_gaps)}")
    print("--------------------------------------------")
    print("  ✅ PASS: test_timeframe_engine_evaluation Passed!")

if __name__ == "__main__":
    test_timeframe_engine_evaluation()
