"""
APEX Quant OS - Master Domain 1 Integration Test
Verifies end-to-end compilation of the unified MarketState object.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy
from market_language.state_compiler import Domain1Compiler


def test_market_state_integration():
    print("Executing Master Domain 1 Integration Test...")

    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 100.5, 100),  # Bar 0
        Candle(2000, 100.5, 101.0, 97.0, 97.5, 100),   # Bar 1: Bearish OB Candle
        Candle(3000, 97.5,  110.0, 97.0, 109.0, 300),  # Bar 2: Displacement Candle
        Candle(4000, 109.0, 120.0, 105.0, 118.0, 300), # Bar 3: FVG Bar 3
        Candle(5000, 118.0, 117.0, 108.0, 109.0, 100), # Bar 4: Pullback Low
        Candle(6000, 109.0, 125.0, 108.0, 124.0, 300), # Bar 5: Continuation Breakout
        Candle(7000, 124.0, 123.0, 115.0, 116.0, 100), # Bar 6: Trailing Padding Bar
    ]

    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = Domain1Compiler(policy=policy)
    
    state = compiler.compile(candles, symbol="BTCUSDT", timeframe="1H")

    assert state.symbol == "BTCUSDT"
    assert state.last_close == 116.0
    assert len(state.structure.internal_swings) >= 1, "Expected internal swings"
    assert len(state.fair_value_gaps) >= 1, "Expected Fair Value Gaps"
    assert state.phase is not None, "Expected valid MarketPhase"

    print("\n--- UNIFIED MARKET STATE SNAPSHOT VERIFIED ---")
    print(f" Symbol:              {state.symbol} ({state.timeframe})")
    print(f" Last Close:          ${state.last_close:.2f}")
    print(f" Trend Direction:     {state.structure.trend.direction.value}")
    print(f" Market Phase:        {state.phase.value}")
    print(f" Equal Levels Found:  {len(state.equal_levels)}")
    print(f" Fair Value Gaps:     {len(state.fair_value_gaps)}")
    print(f" Order Blocks Found:  {len(state.order_blocks)}")
    print(f" Is Premium / Discount: Premium={state.is_premium} | Discount={state.is_discount}")
    print("----------------------------------------------")
    print("  ✅ PASS: Master Domain 1 Market State Integration Test Passed!")


if __name__ == "__main__":
    test_market_state_integration()
