# Component Manifest Contract Header
__module_name__ = "stateless_keyzone_imbalance_calculator"
__build_version__ = "5.2.0-stable"
__spec_contract_hash__ = "0x21_keyzone_calculator_core"
__regression_suite_hash__ = "0x21_keyzone_calculator_verify"

from typing import List, Dict, Any

class KeyzoneCalculator:
    """Stateless math engine detecting institutional Order Blocks and Fair Value Gap imbalances."""

    def calculate_keyzones(self, candles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Scans price arrays and maps structural pricing imbalance matrices."""
        fvgs = []
        order_blocks = []

        if len(candles) < 3:
            return {"fvgs": fvgs, "order_blocks": order_blocks}

        # 1. Detect Fair Value Gaps (3-Candle Sequence Sweeps)
        for i in range(2, len(candles)):
            # Bullish Imbalance Invariance Check
            if candles[i]["low"] > candles[i-2]["high"]:
                fvgs.append({
                    "type": "BULLISH_FVG",
                    "top": candles[i]["low"],
                    "bottom": candles[i-2]["high"],
                    "origin_timestamp": candles[i-1]["timestamp"]
                })

            # Bearish Imbalance Invariance Check
            elif candles[i]["high"] < candles[i-2]["low"]:
                fvgs.append({
                    "type": "BEARISH_FVG",
                    "top": candles[i-2]["low"],
                    "bottom": candles[i]["high"],
                    "origin_timestamp": candles[i-1]["timestamp"]
                })

        # 2. Detect Validated Order Blocks (Linked strictly to displacement momentum)
        for i in range(0, len(candles) - 2):
            # Bullish Order Block: Bearish candle followed by an explosive Bullish FVG launch
            if candles[i]["close"] < candles[i]["open"]:
                # Check if subsequent candles form a confirmed Bullish FVG imbalance
                has_displacement = (
                    candles[i+2]["low"] > candles[i]["high"] or 
                    (i + 3 < len(candles) and candles[i+3]["low"] > candles[i+1]["high"])
                )
                if has_displacement:
                    order_blocks.append({
                        "type": "DEMAND_OB",
                        "high": candles[i]["high"],
                        "low": candles[i]["low"],
                        "timestamp": candles[i]["timestamp"]
                    })

            # Bearish Order Block: Bullish candle followed by an explosive Bearish FVG drop
            elif candles[i]["close"] > candles[i]["open"]:
                has_displacement = (
                    candles[i+2]["high"] < candles[i]["low"] or
                    (i + 3 < len(candles) and candles[i+3]["high"] < candles[i+1]["low"])
                )
                if has_displacement:
                    order_blocks.append({
                        "type": "SUPPLY_OB",
                        "high": candles[i]["high"],
                        "low": candles[i]["low"],
                        "timestamp": candles[i]["timestamp"]
                    })

        return {"fvgs": fvgs, "order_blocks": order_blocks}

keyzone_calculator = KeyzoneCalculator()
