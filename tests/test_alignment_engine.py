"""
APEX Quant OS - Unit Test: AlignmentEngine
Verifies HTF -> MTF -> LTF trend alignment and setup validation.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from market_language.market_structure import Candle
from market_language.timeframe_engine import TimeframeEngine
from strategy.alignment_engine import AlignmentEngine, BiasDirection


def test_alignment_evaluation():
    print("Executing tests/test_alignment_engine.py...")

    candles = [
        Candle(1000, 100.0, 102.0, 99.0, 100.5, 100),
        Candle(2000, 100.5, 101.0, 97.0, 97.5, 100),
        Candle(3000, 97.5,  110.0, 97.0, 109.0, 300),
        Candle(4000, 109.0, 120.0, 105.0, 118.0, 300),
        Candle(5000, 118.0, 117.0, 108.0, 109.0, 100),
        Candle(6000, 109.0, 125.0, 108.0, 124.0, 300),
        Candle(7000, 124.0, 123.0, 115.0, 116.0, 100),
    ]

    tf_engine = TimeframeEngine()
    htf_state = tf_engine.evaluate(candles, timeframe="4H")
    mtf_state = tf_engine.evaluate(candles, timeframe="1H")
    ltf_state = tf_engine.evaluate(candles, timeframe="15M")

    result = AlignmentEngine.evaluate_alignment("SET_4_INTRADAY", htf_state, mtf_state, ltf_state)

    assert result.htf_bias == BiasDirection.BULLISH
    assert result.mtf_aligned is True
    assert result.ltf_trigger is True
    assert result.is_setup_valid is True

    print("\n--- MULTI-TIMEFRAME ALIGNMENT VERIFIED ---")
    print(f" Timeframe Set:    {result.set_id}")
    print(f" HTF Bias:         {result.htf_bias.value}")
    print(f" MTF Aligned:      {result.mtf_aligned}")
    print(f" LTF Trigger:      {result.ltf_trigger}")
    print(f" Valid Trade Setup: {result.is_setup_valid}")
    print(f" Decision Reason:  {result.reason}")
    print("--------------------------------------------")
    print("  ✅ PASS: test_alignment_evaluation Passed!")


if __name__ == "__main__":
    test_alignment_evaluation()
