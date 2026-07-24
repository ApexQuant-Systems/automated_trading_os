"""
APEX Quant OS - Engine 6 Unit Tests: AnchorEngine
Tests Causal Origin Traceback and Protected Strong vs Weak Anchor assignment.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.models import SwingLifecycleState


def test_causal_strong_anchor_protection():
    candles = [
        Candle(500,  102.0, 103.0, 101.0, 102.0, 100),  # Boundary padding
        Candle(1000, 102.0, 101.0, 95.0,  99.0,  100),  # Causal Low @ 95.0
        Candle(2000, 99.0,  105.0, 98.0,  104.0, 100),
        Candle(3000, 104.0, 110.0, 103.0, 108.0, 100),  # Old High @ 110.0
        Candle(4000, 108.0, 107.0, 102.0, 103.0, 100),
        Candle(5000, 103.0, 116.0, 102.0, 115.0, 300),  # Breakout
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.anchors.protected_low is not None, "Expected Protected Low anchor"
    assert state.anchors.protected_low.price_point.price == 95.0, f"Expected 95.0, got {state.anchors.protected_low.price_point.price}"
    assert state.anchors.protected_low.lifecycle == SwingLifecycleState.PROTECTED_STRONG, "Expected PROTECTED_STRONG lifecycle"
    print("  ✅ PASS: test_causal_strong_anchor_protection")


if __name__ == "__main__":
    print("Executing tests/test_anchor_engine.py...")
    test_causal_strong_anchor_protection()
