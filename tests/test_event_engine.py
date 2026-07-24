"""
APEX Quant OS - Engine 3 Unit Tests: EventEngine
Tests True Displacement BOS, CHOCH, and Rejection Sweeps.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import EventType


def test_displacement_bos_vs_wick_sweep():
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 101.0, 100),
        Candle(2000, 101.0, 106.0, 100.0, 105.0, 100),
        Candle(3000, 105.0, 110.0, 104.0, 108.0, 100),  # High @ 110.0
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 105.0, 101.0, 102.0, 100),
        Candle(6000, 102.0, 111.0, 101.0, 108.0, 100),  # Wick Sweep (High=111, Close=108)
        Candle(7000, 108.0, 115.0, 107.0, 114.0, 200),  # Body Break (Close=114)
    ]
    policy = MarketStructurePolicy(fractal_left_bars=2, fractal_right_bars=2, break_confirmation="STRICT_BODY")
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    rejection_events = [e for e in state.recent_events if e.event_type == EventType.STRUCTURAL_REJECTION]
    assert len(rejection_events) >= 1, "Expected STRUCTURAL_REJECTION event"

    break_events = [e for e in state.recent_events if e.event_type in [EventType.EXTERNAL_BOS_BULLISH, EventType.EXTERNAL_CHOCH_BULLISH]]
    assert len(break_events) >= 1, "Expected Structural Break event"
    print("  ✅ PASS: test_displacement_bos_vs_wick_sweep")


if __name__ == "__main__":
    print("Executing tests/test_event_engine.py...")
    test_displacement_bos_vs_wick_sweep()
