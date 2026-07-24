import os

os.makedirs('strategy', exist_ok=True)
os.makedirs('tests', exist_ok=True)

alignment_code = """\"\"\"
APEX Quant OS - Strategy Alignment Engine
Evaluates HTF Bias -> MTF Setup -> LTF Entry across fractal TimeframeStates.
\"\"\"

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from market_language.timeframe_engine import TimeframeState


class BiasDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True)
class AlignmentResult:
    set_id: str
    htf_bias: BiasDirection
    mtf_aligned: bool
    ltf_trigger: bool
    is_setup_valid: bool
    reason: str


class AlignmentEngine:
    \"\"\"
    Evaluates multi-timeframe alignment across HTF, MTF, and LTF states.
    \"\"\"

    @staticmethod
    def evaluate_alignment(
        set_id: str,
        htf_state: TimeframeState,
        mtf_state: TimeframeState,
        ltf_state: TimeframeState
    ) -> AlignmentResult:
        # 1. Evaluate HTF Bias
        htf_bias = BiasDirection.NEUTRAL
        if htf_state.trend_direction == "BULLISH":
            htf_bias = BiasDirection.BULLISH
        elif htf_state.trend_direction == "BEARISH":
            htf_bias = BiasDirection.BEARISH

        if htf_bias == BiasDirection.NEUTRAL:
            return AlignmentResult(
                set_id=set_id,
                htf_bias=htf_bias,
                mtf_aligned=False,
                ltf_trigger=False,
                is_setup_valid=False,
                reason="HTF Bias is Neutral"
            )

        # 2. Evaluate MTF Alignment
        mtf_aligned = (mtf_state.trend_direction == htf_state.trend_direction)

        # 3. Evaluate LTF Entry Trigger
        ltf_trigger = (ltf_state.trend_direction == htf_state.trend_direction)

        is_setup_valid = mtf_aligned and ltf_trigger

        reason = "Full HTF->MTF->LTF Alignment Confirmed" if is_setup_valid else "Awaiting Timeframe Realignment"

        return AlignmentResult(
            set_id=set_id,
            htf_bias=htf_bias,
            mtf_aligned=mtf_aligned,
            ltf_trigger=ltf_trigger,
            is_setup_valid=is_setup_valid,
            reason=reason
        )
"""

test_alignment_code = """\"\"\"
APEX Quant OS - Unit Test: AlignmentEngine
Verifies HTF -> MTF -> LTF trend alignment and setup validation.
\"\"\"

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

    print("\\n--- MULTI-TIMEFRAME ALIGNMENT VERIFIED ---")
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
"""

with open('strategy/alignment_engine.py', 'w') as f:
    f.write(alignment_code)

with open('tests/test_alignment_engine.py', 'w') as f:
    f.write(test_alignment_code)

print("  ✅ SUCCESS: Strategy Alignment Engine & Unit Test generated cleanly!")
