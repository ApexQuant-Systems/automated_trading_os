# Component Manifest Contract Header
__module_name__ = "universal_market_regime_classifier"
__build_version__ = "5.7.0-stable"
__spec_contract_hash__ = "0x25_regime_classifier_core"
__regression_suite_hash__ = "0x25_regime_classifier_verify"

from typing import List, Dict, Any

class MarketRegimeClassifier:
    """Stateless statistical engine classifying volatility states and structural market regimes."""

    def classify_regime(self, candles: List[Dict[str, Any]], window: int = 5) -> Dict[str, Any]:
        """Evaluates historical volatility ratios to define active capital-allocation filters."""
        if len(candles) < 10:
            return {"classification": "HORIZONTAL_RANGE", "volatility_ratio": 1.0}

        # 1. Compute True Range Arrays
        tr_elements = []
        for i in range(1, len(candles)):
            c_high = candles[i]["high"]
            c_low = candles[i]["low"]
            prev_close = candles[i-1]["close"]
            
            tr = max(
                c_high - c_low,
                abs(c_high - prev_close),
                abs(c_low - prev_close)
            )
            tr_elements.append(tr)

        # 2. Extract relative volatility thresholds
        recent_vol = sum(tr_elements[-window:]) / window
        baseline_vol = sum(tr_elements) / len(tr_elements)
        
        volatility_ratio = recent_vol / baseline_vol if baseline_vol > 0 else 1.0

        # 3. Apply Regime Allocation State Routing Checks
        classification = "HORIZONTAL_RANGE"
        
        if volatility_ratio > 2.5:
            classification = "HIGH_VOLATILITY_SHOCK"
        elif volatility_ratio < 0.5:
            classification = "LOW_VOLATILITY_COMPRESSION"
        else:
            # Evaluate trend direction relative to opening coordinates
            if candles[-1]["close"] > candles[-5]["close"]:
                classification = "TRENDING_BULL"
            elif candles[-1]["close"] < candles[-5]["close"]:
                classification = "TRENDING_BEAR"

        return {
            "classification": classification,
            "volatility_ratio": round(volatility_ratio, 2)
        }

regime_classifier = MarketRegimeClassifier()
