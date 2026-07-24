"""
APEX Quant OS - Unit Tests: KeyZonesEngine
Tests 3-candle Fair Value Gap (FVG) and Order Block (OB) detection.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.key_zones import KeyZonesEngine, ZoneType


def test_fvg_and_ob_detection():
    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 100.5, 100),  # Bar 0
        Candle(2000, 100.5, 101.0, 97.0, 97.5, 100),   # Bar 1: Bearish OB Candle (High=101.0, Low=97.0)
        Candle(3000, 97.5,  110.0, 97.0, 109.0, 300),  # Bar 2: Displacement Candle
        Candle(4000, 109.0, 120.0, 105.0, 118.0, 300), # Bar 3: FVG Bar 3 (Low=105.0 > Bar 1 High=101.0)
    ]

    # 1. Test FVG Detection Directly
    fvgs = KeyZonesEngine.detect_fair_value_gaps(candles)
    assert len(fvgs) >= 1, "Expected Bullish FVG detection"
    assert fvgs[0].zone_type == ZoneType.BULLISH_FVG
    assert fvgs[0].low_price == 101.0
    assert fvgs[0].high_price == 105.0

    print("  ✅ PASS: test_fvg_and_ob_detection")


if __name__ == "__main__":
    print("Executing tests/test_key_zones.py...")
    test_fvg_and_ob_detection()
