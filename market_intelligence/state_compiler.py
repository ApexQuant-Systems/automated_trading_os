# Component Manifest Contract Header
__module_name__ = "unified_market_state_compiler"
__build_version__ = "5.4.1-stable"
__spec_contract_hash__ = "0x23_state_compiler_core"
__regression_suite_hash__ = "0x23_state_compiler_verify"

from typing import List, Dict, Any
from market_intelligence.structure_parser import structure_parser
from market_intelligence.keyzone_calculator import keyzone_calculator
from market_intelligence.liquidity_detector import liquidity_detector
from market_intelligence.phase_classifier import phase_classifier

class MarketStateCompiler:
    """Orchestrates and flattens independent market intelligence vectors into unified state payloads."""

    def compile_timeframe_state(self, candles: List[Dict[str, Any]], asset_name: str, timeframe: str) -> Dict[str, Any]:
        """Synthesizes raw candles into a standardized behavioral language dictionary contract."""
        if len(candles) < 5:
            return {"asset": asset_name, "timeframe": timeframe, "status": "INSUFFICIENT_DATA"}

        # 1. Parse structural breaks, trends, and swing geometries
        parsed_candles = structure_parser.parse_structure(candles)
        
        swing_highs = [c["high"] for c in parsed_candles if c.get("structure_type") == "SWING_HIGH"]
        swing_lows = [c["low"] for c in parsed_candles if c.get("structure_type") == "SWING_LOW"]

        # 2. Extract institutional pricing imbalances (OB & FVG)
        keyzone_payload = keyzone_calculator.calculate_keyzones(candles)

        # 3. Assess active sweep parameters using the terminal candle index
        active_candle = candles[-1]
        liquidity_sweep_snapshot = liquidity_detector.detect_sweeps(active_candle, swing_highs, swing_lows)

        # 4. Deterministic Trend Calculation Layer (Replaces placeholder logic)
        current_trend = "RANGING"
        last_break = "NONE"
        
        # Scan backward to identify the most recent valid structural market direction signal
        for c in reversed(parsed_candles):
            if "break_event" in c:
                last_break = c["break_event"]
                if last_break in ["BOS", "CHOCH"]:
                    current_trend = "BULLISH" if c["close"] > c["open"] else "BEARISH"
                break
        
        # Override with pure structural extreme boundaries if no breaks have occurred yet
        if current_trend == "RANGING" and swing_highs and swing_lows:
            if active_candle["close"] > swing_highs[-1]:
                current_trend = "BULLISH"
            elif active_candle["close"] < swing_lows[-1]:
                current_trend = "BEARISH"

        # 5. Extract current market cycle phase using the phase engine
        active_phase = phase_classifier.classify_phase(parsed_candles)

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
            "market_phase": active_phase
        }

state_compiler = MarketStateCompiler()
