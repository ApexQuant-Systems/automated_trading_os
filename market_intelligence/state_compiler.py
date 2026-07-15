# Component Manifest Contract Header
__module_name__ = "unified_market_state_compiler"
__build_version__ = "5.4.0-stable"
__spec_contract_hash__ = "0x23_state_compiler_core"
__regression_suite_hash__ = "0x23_state_compiler_verify"

from typing import List, Dict, Any
from market_intelligence.structure_parser import structure_parser
from market_intelligence.keyzone_calculator import keyzone_calculator
from market_intelligence.liquidity_detector import liquidity_detector

class MarketStateCompiler:
    """Orchestrates and flattens independent market intelligence vectors into unified state payloads."""

    def compile_timeframe_state(self, candles: List[Dict[str, Any]], asset_name: str, timeframe: str) -> Dict[str, Any]:
        """Synthesizes raw candles into a standardized behavioral language dictionary contract."""
        if len(candles) < 5:
            return {"asset": asset_name, "timeframe": timeframe, "status": "INSUFFICIENT_DATA"}

        # 1. Parse structural breaks, trends, and swing geometries
        parsed_candles = structure_parser.parse_structure(candles)
        
        # Extract historical swing coordinates for the liquidity module
        swing_highs = [c["high"] for c in parsed_candles if c.get("structure_type") == "SWING_HIGH"]
        swing_lows = [c["low"] for c in parsed_candles if c.get("structure_type") == "SWING_LOW"]

        # 2. Extract institutional pricing imbalances (OB & FVG)
        keyzone_payload = keyzone_calculator.calculate_keyzones(candles)

        # 3. Assess active sweep parameters using the terminal candle index
        active_candle = candles[-1]
        liquidity_sweep_snapshot = liquidity_detector.detect_sweeps(active_candle, swing_highs, swing_lows)

        # Determine current primary structural bias
        current_trend = "BULLISH"
        last_break = "NONE"
        for c in reversed(parsed_candles):
            if "break_event" in c:
                last_break = c["break_event"]
                break

        # 4. Standardized Market Payload Data Contract Output Formulation
        return {
            "timestamp": active_candle.get("timestamp", 0),
            "asset_name": asset_name,
            "timeframe": timeframe,
            "trend_state": current_trend,
            "structure_coordinates": {
                "active_swing_highs": swing_highs[-2:] if swing_highs else [],
                "active_swing_lows": swing_lows[-2:] if swing_lows else [],
                "last_break_type": last_break
            },
            "active_keyzones": keyzone_payload["fvgs"] + keyzone_payload["order_blocks"],
            "mapped_liquidity_pools": liquidity_sweep_snapshot,
            "market_phase": "CONTINUATION" if last_break == "BOS" else "COMPRESSION"
        }

state_compiler = MarketStateCompiler()
