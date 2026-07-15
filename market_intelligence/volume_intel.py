# Component Manifest Contract Header
__module_name__ = "stateless_volume_intelligence_core"
__build_version__ = "5.8.0-stable"
__spec_contract_hash__ = "0x26_volume_intel_core"
__regression_suite_hash__ = "0x26_volume_intel_verify"

from typing import List, Dict, Any

class VolumeIntelligenceCore:
    """Stateless math layer quantifying transactional volume drift and institutional flow profiles."""

    def calculate_volume_metrics(self, candles: List[Dict[str, Any]], window: int = 10) -> Dict[str, Any]:
        """Scans localized trading volume arrays to isolate institutional activity signatures."""
        if len(candles) < window + 1:
            return {"relative_volume_ratio": 1.0, "order_flow_imbalance": "NORMAL_VOLUME"}

        active_candle = candles[-1]
        active_vol = float(active_candle["volume"])

        # Extract baseline tracking volume window
        historical_volumes = [float(c["volume"]) for c in candles[-(window+1):-1]]
        mean_baseline_vol = sum(historical_volumes) / len(historical_volumes)

        # Derive relative volume factor index
        rvol = active_vol / mean_baseline_vol if mean_baseline_vol > 0 else 1.0

        # Categorize systemic order flow imbalance signatures
        is_bullish = active_candle["close"] >= active_candle["open"]
        
        if rvol > 1.75:
            imbalance = "BUY_DOMINANT_EXPANSION" if is_bullish else "SELL_DOMINANT_EXPANSION"
        elif rvol < 0.50:
            imbalance = "LOW_LIQUIDITY_DRAIN"
        else:
            imbalance = "NORMAL_VOLUME"

        return {
            "relative_volume_ratio": round(rvol, 2),
            "order_flow_imbalance": imbalance
        }

volume_intel = VolumeIntelligenceCore()
