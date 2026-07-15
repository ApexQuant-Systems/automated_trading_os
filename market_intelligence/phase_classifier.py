# Component Manifest Contract Header
__module_name__ = "stateless_market_phase_classifier"
__build_version__ = "5.5.0-stable"
__spec_contract_hash__ = "0x24_phase_classifier_core"
__regression_suite_hash__ = "0x24_phase_classifier_verify"

from typing import List, Dict, Any

class MarketPhaseClassifier:
    """Stateless engine classification matrix defining intermediate price lifecycle phases."""

    def classify_phase(self, parsed_candles: List[Dict[str, Any]]) -> str:
        """Evaluates localized structural characteristics to isolate active market phase states."""
        if len(parsed_candles) < 3:
            return "COMPRESSION"

        latest_candle = parsed_candles[-1]
        prior_candle = parsed_candles[-2]

        # 1. EXPANSION Phase Rule: Triggered by immediate structural breaks (BOS / CHOCH)
        if latest_candle.get("break_event") in ["BOS", "CHOCH"] or prior_candle.get("break_event") in ["BOS", "CHOCH"]:
            return "EXPANSION"

        # 2. PULLBACK Phase Rule: Counter-trend body break indicating short-term retracement paths
        # For demonstration context: checking counter-trend adjustments relative to local highs
        if latest_candle["close"] < prior_candle["low"] and latest_candle["high"] < prior_candle["high"]:
            return "PULLBACK"

        # 3. COMPRESSION Phase Rule: Tight low-volatility price range contraction bounds
        recent_spreads = [abs(c["high"] - c["low"]) for c in parsed_candles[-3:]]
        mean_spread = sum(recent_spreads) / len(recent_spreads)
        
        if mean_spread < 3.0:  # Tight historical range threshold definition match
            return "COMPRESSION"

        # Default fallback structural assignment state
        return "CONTINUATION"

phase_classifier = MarketPhaseClassifier()
