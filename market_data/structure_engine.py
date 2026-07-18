# Component Manifest Contract Header
__module_name__ = "market_data.structure_engine"
__specification_version__ = "v1.0-frozen"
__implementation_version__ = "v1.0-stateless-core"

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
    """Stateless multi-tier structural breakout engine utilizing chronological Dealing Range anchors."""

    def classify_swings(self, swings: List[Dict[str, Any]], config: Dict[str, Any], timeframe: str) -> List[Dict[str, Any]]:
        """Module 2.2.1: Classifies raw geometric swing facts into major external or minor internal structures."""
        ont_params = config["market_ontology_parameters"]
        tf_clean = timeframe.lower()
        macro_n = ont_params["timeframe_swing_windows"].get(tf_clean, 2)
        
        classified_swings = []
        for s in swings:
            updated_swing = s.copy()
            # If the fact matches or exceeds the primary macro timeframe lookback window, it is External Major
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
        """Module 2.2.2 & 2.2.3: Detects breakouts via candle body closes and outputs deterministic trend status."""
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

        # Setup runtime state parameters tracking the dynamic dealing range context
        current_regime: Literal["BULLISH", "BEARISH", "RANGE", "UNKNOWN"] = "UNKNOWN"
        last_event_type: Literal["BOS", "MSS", "CHOCH", "INITIALIZATION"] = "INITIALIZATION"
        last_event_id = "INIT"
        
        # Chronological range anchors
        active_high: Optional[float] = None
        active_low: Optional[float] = None
        broken_high_id = ""
        broken_low_id = ""
        
        # Track historical structural extreme references for CHOCH calculation loops
        highest_high_peak_ob = -1.0
        lowest_low_trough_ob = float('inf')
        
        # Sort swings by timestamp to step chronologically through data blocks
        sorted_swings = sorted(classified_swings, key=lambda x: x["timestamp"])
        
        # Establish primitive baseline boundaries from initial discovered major swings
        major_highs = [s for s in sorted_swings if s["classification"] == "EXTERNAL_MAJOR" and s["swing_type"] == "HIGH"]
        major_lows = [s for s in sorted_swings if s["classification"] == "EXTERNAL_MAJOR" and s["swing_type"] == "LOW"]
        
        if major_highs:
            active_high = major_highs[0]["price"]
            broken_high_id = major_highs[0]["swing_id"]
        if major_lows:
            active_low = major_lows[0]["price"]
            broken_low_id = major_lows[0]["swing_id"]
            
        if active_high and active_low:
            current_regime = "RANGE"
            evidence.append(f"Initial range baseline locked between Low={active_low} and High={active_high}")

        # Map candles by timestamp for high-speed chronological coordinate checking
        candle_map = {c["timestamp"]: c for c in candles}
        sorted_timestamps = sorted(list(candle_map.keys()))
        
        # Track internal shifts
        last_minor_high: Optional[float] = None
        last_minor_low: Optional[float] = None
        active_mss_id: Optional[str] = None

        # Chronological execution sweep loop
        for ts in sorted_timestamps:
            candle = candle_map[ts]
            c_close = candle["close"]
            
            # Check if any new swing factor was confirmed at this exact timestamp (Look-ahead protection gate)
            current_confirmed_swings = [s for s in sorted_swings if s["confirmed_at_ts"] == ts]
            for cs in current_confirmed_swings:
                if cs["classification"] == "EXTERNAL_MAJOR":
                    if cs["swing_type"] == "HIGH":
                        active_high = cs["price"]
                        broken_high_id = cs["swing_id"]
                        highest_high_peak_ob = max(highest_high_peak_ob, cs["price"])
                        evidence.append(f"[{ts}] New Major Range High Anchor logged: {active_high}")
                    else:
                        active_low = cs["price"]
                        broken_low_id = cs["swing_id"]
                        lowest_low_trough_ob = min(lowest_low_trough_ob, cs["price"])
                        evidence.append(f"[{ts}] New Major Range Low Anchor logged: {active_low}")
                else:
                    if cs["swing_type"] == "HIGH":
                        last_minor_high = cs["price"]
                    else:
                        last_minor_low = cs["price"]

            # Evaluate structural breakouts against boundary anchors
            if current_regime in ["BULLISH", "RANGE"] and active_high and c_close - active_high > epsilon:
                # Check for structural trend reversal condition (CHOCH) or expansion (BOS)
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
                
                # Dynamic Dealing Range Reset: Fluid high hunt initiated, recalculate baseline Low coordinate
                # Find minimum low between broken swing timestamp and current execution mark
                range_candles = [c for c in candles if cs["timestamp"] <= c["timestamp"] <= ts]
                if range_candles:
                    active_low = min([c["low"] for c in range_candles])
                active_high = None  # Liquidated upper bound boundary until next confirmation block
                
            elif current_regime in ["BEARISH", "RANGE"] and active_low and active_low - c_close > epsilon:
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
                
                # Recalculate range metrics
                range_candles = [c for c in candles if cs["timestamp"] <= c["timestamp"] <= ts]
                if range_candles:
                    active_high = max([c["high"] for c in range_candles])
                active_low = None
                
            # Early Momentum Market Structure Shift (MSS) verification engine tracking
            elif current_regime == "BEARISH" and last_minor_high and c_close - last_minor_high > epsilon:
                evt_id = f"{symbol.upper()}-{timeframe.upper()}-MSS-{ts}"
                active_mss_id = evt_id
                evidence.append(f"[{ts}] Early Momentum Bullish MSS alert triggered at price {c_close}")
                last_minor_high = None # Expire minor target after breakout clear
                
            elif current_regime == "BULLISH" and last_minor_low and last_minor_low - c_close > epsilon:
                evt_id = f"{symbol.upper()}-{timeframe.upper()}-MSS-{ts}"
                active_mss_id = evt_id
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
                "evidence_chain": evidence[-5:]  # Return the five most recent factual context lines
            }
        }
