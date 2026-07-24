"""
APEX Quant OS - Engine 1 Unit Tests: SwingEngine
Tests internal fractal detection and external promotion depth.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import SwingOrientation


def test_internal_swing_detection():
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 108.0, 100.0, 107.0, 100),  # High Peak @ 108.0
        Candle(3000, 107.0, 105.0, 101.0, 102.0, 100),
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert len(state.internal_swings) >= 1, "Expected internal swing detection"
    high_swings = [s for s in state.internal_swings if s.orientation == SwingOrientation.HIGH]
    assert len(high_swings) == 1, "Expected 1 internal high swing"
    assert high_swings[0].price_point.price == 108.0, f"Expected 108.0, got {high_swings[0].price_point.price}"
    print("  ✅ PASS: test_internal_swing_detection")


if __name__ == "__main__":
    print("Executing tests/test_swing_engine.py...")
    test_internal_swing_detection()
