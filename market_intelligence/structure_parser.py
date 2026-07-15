# Component Manifest Contract Header
__module_name__ = "stateless_market_structure_parser"
__build_version__ = "5.1.0-stable"
__spec_contract_hash__ = "0x20_structure_parser_core"
__regression_suite_hash__ = "0x20_structure_parser_verify"

from typing import List, Dict, Any

class MarketStructureParser:
    """Pure mathematical engine parsing trend direction, swing points, BOS, and CHOCH mappings."""

    def parse_structure(self, candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a chronological candle array and appends pure structural tokens."""
        if len(candles) < 5:
            return candles

        # Deep clone list to maintain state mutation protections
        output = [dict(c) for c in candles]
        
        # Operational state memory
        current_trend = "BULLISH" # Default baseline state initialization
        last_high_idx = -1
        last_low_idx = -1
        
        # Track confirmed absolute structural extreme price points
        confirmed_swing_high = float('inf')
        confirmed_swing_low = float('-inf')

        # Run historical scanning array up to length boundary limits
        for i in range(2, len(output) - 2):
            # 1. 5-Candle Fractal Swing High Verification Logic
            is_swing_high = (
                output[i]["high"] > output[i-1]["high"] and
                output[i]["high"] > output[i-2]["high"] and
                output[i]["high"] > output[i+1]["high"] and
                output[i]["high"] > output[i+2]["high"]
            )

            # 2. 5-Candle Fractal Swing Low Verification Logic
            is_swing_low = (
                output[i]["low"] < output[i-1]["low"] and
                output[i]["low"] < output[i-2]["low"] and
                output[i]["low"] < output[i+1]["low"] and
                output[i]["low"] < output[i+2]["low"]
            )

            if is_swing_high:
                output[i]["structure_type"] = "SWING_HIGH"
                last_high_idx = i
                confirmed_swing_high = output[i]["high"]

            elif is_swing_low:
                output[i]["structure_type"] = "SWING_LOW"
                last_low_idx = i
                confirmed_swing_low = output[i]["low"]
            else:
                output[i]["structure_type"] = "NORMAL"

            # 3. Dynamic Break of Structure (BOS) & Change of Character (CHOCH) Tracking Matrix
            # Trigger conditions evaluate at the current candle's CLOSE parameter
            current_close = output[i+2]["close"]

            if current_trend == "BULLISH":
                # Trend Continuation: Close breaks above prior confirmed Swing High
                if last_high_idx != -1 and current_close > confirmed_swing_high:
                    output[i+2]["break_event"] = "BOS"
                    confirmed_swing_high = float('inf') # Reset anchor once broken
                
                # Trend Reversal: Close breaks below prior confirmed Swing Low
                elif last_low_idx != -1 and current_close < confirmed_swing_low:
                    output[i+2]["break_event"] = "CHOCH"
                    current_trend = "BEARISH"
                    confirmed_swing_low = float('-inf')

            elif current_trend == "BEARISH":
                # Trend Continuation: Close breaks below prior confirmed Swing Low
                if last_low_idx != -1 and current_close < confirmed_swing_low:
                    output[i+2]["break_event"] = "BOS"
                    confirmed_swing_low = float('-inf')
                
                # Trend Reversal: Close breaks above prior confirmed Swing High
                elif last_high_idx != -1 and current_close > confirmed_swing_high:
                    output[i+2]["break_event"] = "CHOCH"
                    current_trend = "BULLISH"
                    confirmed_swing_high = float('inf')

        return output

structure_parser = MarketStructureParser()
