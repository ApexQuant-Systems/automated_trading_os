# Component Manifest Contract Header
__module_name__ = "market_data.structure_engine"
__specification_version__ = "v1.1-fixed"
__implementation_version__ = "v1.1-stateless-core"

from typing import List, Dict, Any, Literal, TypedDict, Optional

class StructuralEventRecord(TypedDict):
    event_id: str
    event_type: Literal["BOS", "MSS", "CHOCH"]
    direction: Literal["BULLISH", "BEARISH"]
    trigger_timestamp: int
    broken_swing_id: str
    breakout_price: float

class TrendTelemetry(TypedDict):
    symbol: str
    timeframe: str
    current_regime: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"]
    last_event_type: Literal["BOS", "MSS", "CHOCH", "INITIALIZATION"]
    last_event_id: str
    evidence_chain: List[str]

class DeterministicStructureEngine:
    """Stateless multi-tier structural breakout engine utilizing explicit chronological anchors."""

    def classify_swings(self, swings: List[Dict[str, Any]], config: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        """Module 2.2.1: Classifies raw geometric swing facts into major external or minor internal structures."""
        ont_params = config["market_ontology_parameters"]
        tf_clean = timeframe.lower()
        macro_n = ont_params["timeframe_swing_windows"].get(tf_clean, 2)
        
        classified_swings = []
        for s in swings:
            updated_swing = s.copy()
            if s["window_meta"]["configured_n"] >= macro_n:
                updated_swing["status"] = "ACTIVE_RANGE_LIMIT"
                updated_swing["classification"] = "EXTERNAL_MAJOR"
            else:
                updated_swing["classification"] = "INTERNAL_MINOR"
            classified_swings.append(updated_swing)
        return classified_swings

    def process_structure(
        self,
        symbol: str,
        timeframe: str,
        candles: List[Dict[str, Any]],
        classified_swings: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Module 2.2.2 & 2.2.3: Detects breakouts via candle body closes with look-ahead bias shields."""
        epsilon = config["market_ontology_parameters"]["floating_point_epsilon"]
        
        events: List[StructuralEventRecord] = []
        evidence: List[str] = ["Initialization: Structural state analyzer online."]
        
        if len(classified_swings) < 2:
            return {
                "events": events,
                "trend": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "current_regime": "UNKNOWN",
                    "last_event_type": "INITIALIZATION",
                    "last_event_id": "INIT",
                    "evidence_chain": ["Insufficient structural swing anchors to compute dealing horizons."]
                }
            }

        current_regime: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"] = "UNKNOWN"
        last_event_type: Literal["BOS", "MSS", "CHOCH", "INITIALIZATION"] = "INITIALIZATION"
        last_event_id = "INIT"
        
        # Explicitly decoupled structural coordinate anchors
        active_high: Optional[float] = None
        active_high_ts: Optional[int] = None
        broken_high_id = ""
        
        active_low: Optional[float] = None
        active_low_ts: Optional[int] = None
        broken_low_id = ""
        
        # Track the active threshold ceiling/floor during live expansion runs
        expansion_peak: Optional[float] = None
        expansion_trough: Optional[float] = None
        
        sorted_swings = sorted(classified_swings, key=lambda x: x["timestamp"])
        
        major_highs = [s for s in sorted_swings if s["classification"] == "EXTERNAL_MAJOR" and s["swing_type"] == "HIGH"]
        major_lows = [s for s in sorted_swings if s["classification"] == "EXTERNAL_MAJOR" and s["swing_type"] == "LOW"]
        
        if major_highs:
            active_high = major_highs[0]["price"]
            active_high_ts = major_highs[0]["timestamp"]
            broken_high_id = major_highs[0]["swing_id"]
            expansion_peak = active_high
        if major_lows:
            active_low = major_lows[0]["price"]
            active_low_ts = major_lows[0]["timestamp"]
            broken_low_id = major_lows[0]["swing_id"]
            expansion_trough = active_low
            
        if active_high is not None and active_low is not None:
            current_regime = "RANGE"
            evidence.append(f"Initial range baseline locked between Low={active_low} and High={active_high}")

        candle_map = {c["timestamp"]: c for c in candles}
        sorted_timestamps = sorted(list(candle_map.keys()))
        
        last_minor_high: Optional[float] = None
        last_minor_low: Optional[float] = None

        for ts in sorted_timestamps:
            candle = candle_map[ts]
            c_close = candle["close"]
            
            # Look-ahead confirmation gate routing
            current_confirmed_swings = [s for s in sorted_swings if s["confirmed_at_ts"] == ts]
            for cs in current_confirmed_swings:
                if cs["classification"] == "EXTERNAL_MAJOR":
                    if cs["swing_type"] == "HIGH":
                        active_high = cs["price"]
                        active_high_ts = cs["timestamp"]
                        broken_high_id = cs["swing_id"]
                        if current_regime != "BULLISH":
                            expansion_peak = active_high
                        evidence.append(f"[{ts}] New Major Range High Anchor logged: {active_high}")
                    else:
                        active_low = cs["price"]
                        active_low_ts = cs["timestamp"]
                        broken_low_id = cs["swing_id"]
                        if current_regime != "BEARISH":
                            expansion_trough = active_low
                        evidence.append(f"[{ts}] New Major Range Low Anchor logged: {active_low}")
                else:
                    if cs["swing_type"] == "HIGH":
                        last_minor_high = cs["price"]
                    else:
                        last_minor_low = cs["price"]

            # Evaluate structural breakouts against explicit boundary targets
            target_high = expansion_peak if current_regime == "BULLISH" else active_high
            if current_regime in ["BULLISH", "RANGE"] and target_high is not None and c_close - target_high > epsilon:
                ev_type: Literal["BOS", "CHOCH"] = "BOS" if current_regime == "BULLISH" else "CHOCH"
                current_regime = "BULLISH"
                last_event_type = ev_type
                
                evt_id = f"{symbol.upper()}-{timeframe.upper()}-{ev_type}-{ts}"
                last_event_id = evt_id
                
                events.append({
                    "event_id": evt_id,
                    "event_type": ev_type,
                    "direction": "BULLISH",
                    "trigger_timestamp": ts,
                    "broken_swing_id": broken_high_id,
                    "breakout_price": c_close
                })
                
                evidence.append(f"[{ts}] Confirmed Bullish {ev_type} Body Close Breakout clear at price: {c_close}")
                
                # Dynamic Dealing Range Low Reset using fixed anchor tracking bounds
                if active_high_ts is not None:
                    range_candles = [c for c in candles if active_high_ts <= c["timestamp"] <= ts]
                    if range_candles:
                        active_low = min([c["low"] for c in range_candles])
                
                expansion_peak = c_close  # Shift the expansion trail ceiling up dynamically
                active_high = None

            elif current_regime in ["BEARISH", "RANGE"] and expansion_trough is not None and active_low is not None and active_low - c_close > epsilon:
                target_low = expansion_trough if current_regime == "BEARISH" else active_low
                if c_close < target_low - epsilon:
                    ev_type = "BOS" if current_regime == "BEARISH" else "CHOCH"
                    current_regime = "BEARISH"
                    last_event_type = ev_type
                    
                    evt_id = f"{symbol.upper()}-{timeframe.upper()}-{ev_type}-{ts}"
                    last_event_id = evt_id
                    
                    events.append({
                        "event_id": evt_id,
                        "event_type": ev_type,
                        "direction": "BEARISH",
                        "trigger_timestamp": ts,
                        "broken_swing_id": broken_low_id,
                        "breakout_price": c_close
                    })
                    
                    evidence.append(f"[{ts}] Confirmed Bearish {ev_type} Body Close Breakout clear at price: {c_close}")
                    
                    if active_low_ts is not None:
                        range_candles = [c for c in candles if active_low_ts <= c["timestamp"] <= ts]
                        if range_candles:
                            active_high = max([c["high"] for c in range_candles])
                    
                    expansion_trough = c_close
                    active_low = None
                
            # Early Momentum Market Structure Shift (MSS) indicators
            elif current_regime == "BEARISH" and last_minor_high is not None and c_close - last_minor_high > epsilon:
                evt_id = f"{symbol.upper()}-{timeframe.upper()}-MSS-{ts}"
                evidence.append(f"[{ts}] Early Momentum Bullish MSS alert triggered at price {c_close}")
                last_minor_high = None
                
            elif current_regime == "BULLISH" and last_minor_low is not None and last_minor_low - c_close > epsilon:
                evt_id = f"{symbol.upper()}-{timeframe.upper()}-MSS-{ts}"
                evidence.append(f"[{ts}] Early Momentum Bearish MSS alert triggered at price {c_close}")
                last_minor_low = None

        return {
            "events": events,
            "trend": {
                "symbol": symbol,
                "timeframe": timeframe,
                "current_regime": current_regime,
                "last_event_type": last_event_type,
                "last_event_id": last_event_id,
                "evidence_chain": evidence[-5:]
            }
        }
