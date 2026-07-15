# Component Manifest Contract Header
__module_name__ = "stateless_core_strategy_engine"
__build_version__ = "3.1.0-stable"
__spec_contract_hash__ = "0x30_strategy_engine_core"
__regression_suite_hash__ = "0x30_strategy_engine_verify"

from typing import Dict, Any

class CoreStrategyEngine:
    """Stateless evaluation core translating compiled market states into risk-mapped trading vectors."""

    def evaluate_state_rules(self, state: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """Applies programmatic confluence filters to output explicit BUY/SELL/WAIT trade setups."""
        decision = {
            "action": "WAIT",
            "entry_price": 0.0,
            "stop_loss": 0.0,
            "take_profit": 0.0,
            "risk_reward_ratio": 0.0
        }

        trend = state.get("trend_state", "RANGING")
        phase = state.get("market_phase", "COMPRESSION")
        pools = state.get("mapped_liquidity_pools", {})
        struct_coords = state.get("structure_coordinates", {})

        # Extract structural tracking extreme levels for exact invalidation placement
        active_lows = struct_coords.get("active_swing_lows", [])
        active_highs = struct_coords.get("active_swing_highs", [])

        # 1. Programmable LONG Entry Rule Constraints Checklist
        if trend == "BULLISH" and phase in ["PULLBACK", "CONTINUATION"]:
            if pools.get("BULLISH_SWEEP", False) and active_lows:
                sl_level = min(active_lows) - (current_price * 0.001) # Buffer buffer zone adjustment
                risk_distance = current_price - sl_level
                
                if risk_distance > 0:
                    decision["action"] = "BUY"
                    decision["entry_price"] = current_price
                    decision["stop_loss"] = round(sl_level, 4)
                    decision["take_profit"] = round(current_price + (risk_distance * 4.0), 4) # Hardcoded 1:4 Minimum
                    decision["risk_reward_ratio"] = 4.0

        # 2. Programmable SHORT Entry Rule Constraints Checklist
        elif trend == "BEARISH" and phase in ["PULLBACK", "CONTINUATION"]:
            if pools.get("BEARISH_SWEEP", False) and active_highs:
                sl_level = max(active_highs) + (current_price * 0.001)
                risk_distance = sl_level - current_price
                
                if risk_distance > 0:
                    decision["action"] = "SELL"
                    decision["entry_price"] = current_price
                    decision["stop_loss"] = round(sl_level, 4)
                    decision["take_profit"] = round(current_price - (risk_distance * 4.0), 4) # Hardcoded 1:4 Minimum
                    decision["risk_reward_ratio"] = 4.0

        return decision

strategy_engine = CoreStrategyEngine()
