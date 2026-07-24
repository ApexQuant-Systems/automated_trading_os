"""
APEX Quant OS - Strategy Alignment Engine
Evaluates HTF Bias -> MTF Setup -> LTF Entry across fractal TimeframeStates.
"""

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
    """
    Evaluates multi-timeframe alignment across HTF, MTF, and LTF states.
    """

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
