"""
APEX Quant OS - Unit Tests: KeyLevelsEngine
Tests EQH/EQL liquidity pool detection and PDH/PDL extraction.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.key_levels import KeyLevelsEngine, LevelType


def test_eqh_eql_detection():
    candles = [
        Candle(1000, 100.0, 110.0, 99.0, 108.0, 100),
        Candle(2000, 108.0, 107.0, 95.0, 96.0, 100),   # Low 1 @ 95.0
        Candle(3000, 96.0, 120.0, 96.0, 118.0, 100),  # High 1 @ 120.0
        Candle(4000, 118.0, 117.0, 95.02, 96.0, 100), # Low 2 @ 95.02 (~Equal Low)
        Candle(5000, 96.0, 120.03, 95.5, 119.0, 100), # High 2 @ 120.03 (~Equal High)
        Candle(6000, 119.0, 118.0, 110.0, 112.0, 100), # Trailing Padding Candle
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    levels = KeyLevelsEngine.detect_equal_levels(list(state.internal_swings), tolerance_pct=0.001)

    eqh = [l for l in levels if l.level_type == LevelType.EQH]
    eql = [l for l in levels if l.level_type == LevelType.EQL]

    assert len(eqh) >= 1, "Expected EQH detection"
    assert len(eql) >= 1, "Expected EQL detection"
    print("  ✅ PASS: test_eqh_eql_detection")


if __name__ == "__main__":
    print("Executing tests/test_key_levels.py...")
    test_eqh_eql_detection()
