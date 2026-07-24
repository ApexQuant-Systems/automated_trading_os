"""
APEX Quant OS - Engine 7 Unit Tests: BoundaryEngine
Tests Dealing Range computation and 50% Equilibrium price calculation.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler


def test_dealing_range_equilibrium():
    candles = [
        Candle(250,  101.0, 103.0, 100.0, 102.0, 100), # Padding Candle (Index 0)
        Candle(500,  100.0, 102.0, 90.0,  99.0,  100), # LOW ANCHOR @ 90.0 (Index 1)
        Candle(1000, 99.0,  105.0, 98.0,  104.0, 100), # Intermediate Candle (Index 2)
        Candle(2000, 104.0, 150.0, 103.0, 148.0, 300), # HIGH ANCHOR @ 150.0 (Index 3)
        Candle(2500, 148.0, 149.0, 140.0, 142.0, 100), # Padding Candle (Index 4)
    ]
    policy = MarketStructurePolicy(fractal_left_bars=1, fractal_right_bars=1)
    compiler = StructureCompiler(policy=policy)
    state = compiler.compile(candles, symbol="TEST", timeframe="1H")

    assert state.dealing_range is not None, "Expected valid Dealing Range"
    expected_eq = (150.0 + 90.0) / 2.0  # 120.0
    assert state.dealing_range.equilibrium_price == expected_eq, f"Expected EQ={expected_eq}, got {state.dealing_range.equilibrium_price}"
    print("  ✅ PASS: test_dealing_range_equilibrium")


if __name__ == "__main__":
    print("Executing tests/test_boundary_engine.py...")
    test_dealing_range_equilibrium()
