# Component Manifest Contract Header
__module_name__ = "stateless_liquidity_sweep_detector"
__build_version__ = "5.3.0-stable"
__spec_contract_hash__ = "0x22_liquidity_detector_core"
__regression_suite_hash__ = "0x22_liquidity_detector_verify"

from typing import List, Dict, Any

class LiquiditySweepDetector:
    """Stateless mathematical engine identifying liquidity sweeps and institutional stop runs."""

    def detect_sweeps(self, current_candle: Dict[str, Any], swing_highs: List[float], swing_lows: List[float]) -> Dict[str, bool]:
        """Evaluates whether the active candle wick has swept historical liquidity pools."""
        metrics = {"BULLISH_SWEEP": False, "BEARISH_SWEEP": False}
        
        c_high = current_candle["high"]
        c_low = current_candle["low"]
        c_close = current_candle["close"]

        # 1. Bullish Sweep Evaluation (Price pierces below an old low, but closes back above it)
        if swing_lows:
            target_low = min(swing_lows)
            if c_low < target_low and c_close > target_low:
                metrics["BULLISH_SWEEP"] = True

        # 2. Bearish Sweep Evaluation (Price pierces above an old high, but closes back below it)
        if swing_highs:
            target_high = max(swing_highs)
            if c_high > target_high and c_close < target_high:
                metrics["BEARISH_SWEEP"] = True

        return metrics

liquidity_detector = LiquiditySweepDetector()
