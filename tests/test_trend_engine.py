"""
APEX Quant OS - Engine 4 Unit Tests: TrendEngine
Tests trend state transitions, CHOCH flips, and maturity progression.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import TrendDirection


def test_trend_direction_flip():
    candles = [
        Candle(500,  100.0, 105.0, 99.0,  104.0, 100),
        Candle(1000, 104.0, 110.0, 103.0, 109.0, 100), # High @ 110
        Candle(2000, 109.0, 108.0, 101.0, 102.0, 100), # Low @ 101
        Candle(3000, 102.0, 116.0, 101.0, 115.0, 300), # CHOCH Break -> Flips to Bullish
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.trend.direction == TrendDirection.BULLISH, f"Expected BULLISH, got {state.trend.direction}"
    print("  ✅ PASS: test_trend_direction_flip")


if __name__ == "__main__":
    print("Executing tests/test_trend_engine.py...")
    test_trend_direction_flip()
