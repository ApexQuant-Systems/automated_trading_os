# Component Manifest Contract Header
__module_name__ = "market_data.swing_engine"
__specification_version__ = "v1.0-frozen"
__implementation_version__ = "v1.1-stateless"

import hashlib
import json
import time
from typing import List, Dict, Any, Literal, TypedDict, Optional

class WindowMetadata(TypedDict):
    configured_n: int
    left_window_actual: int
    right_window_actual: int

class ProcessingMetadata(TypedDict):
    engine_version: str
    processing_time_ms: float
    dataset_hash_sha256: str

class SwingFactRecord(TypedDict):
    swing_id: str
    job_id: str
    timestamp: int
    swing_type: Literal["HIGH", "LOW"]
    price: float
    index_position: int
    confirmed_at_ts: int
    status: Literal["DISCOVERED"]
    window_meta: WindowMetadata
    metrics: ProcessingMetadata

class DynamicSwingFactEngine:
    """100% Stateless Geometric Extrema Calculator enforcing strict look-ahead bias protections."""

    @staticmethod
    def calculate_dataset_hash(candles: List[Dict[str, Any]]) -> str:
        """Computes a deterministic cryptographic check value for tracking baseline inputs."""
        serialized = json.dumps(candles, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def calculate_swings(
        self, 
        symbol: str, 
        timeframe: str, 
        job_id: str, 
        candles: List[Dict[str, Any]], 
        config: Dict[str, Any]
    ) -> List[SwingFactRecord]:
        """Processes historical price arrays statelessly and extracts immutable structural swing facts."""
        start_wall_clock = time.perf_counter()
        swing_facts: List[SwingFactRecord] = []
        
        if not candles:
            return swing_facts

        # 1. Parse operational configuration filters
        ont_params = config["market_ontology_parameters"]
        epsilon = ont_params["floating_point_epsilon"]
        outage_multiplier = ont_params["missing_data_threshold_multiplier"]
        tie_mode = ont_params["tie_breaker_mode"]
        
        tf_clean = timeframe.lower()
        n = ont_params["timeframe_swing_windows"].get(tf_clean, 2)
        
        total_candles = len(candles)
        dataset_hash = self.calculate_dataset_hash(candles)
        
        # Determine timeframe primitive delta metrics to flag connection gaps
        if total_candles > 1:
            base_deltas = [candles[i]["timestamp"] - candles[i-1]["timestamp"] for i in range(1, min(11, total_candles))]
            expected_delta = min(base_deltas) if base_deltas else 900
        else:
            expected_delta = 900

        # 2. Iterate sequentially while respecting dataset edge boundaries
        for i in range(n, total_candles - n):
            candidate = candles[i]
            candidate_high = candidate["high"]
            candidate_low = candidate["low"]
            candidate_ts = candidate["timestamp"]
            
            # A. Enforce Missing Data Outage Discontinuity Verification Checks
            window_slice = candles[i - n : i + n + 1]
            outage_detected = False
            for k in range(1, len(window_slice)):
                if (window_slice[k]["timestamp"] - window_slice[k-1]["timestamp"]) > (expected_delta * outage_multiplier):
                    outage_detected = True
                    break
            
            if outage_detected:
                continue

            # B. Evaluate Pure Swing High Geometry Rules
            is_swing_high = True
            for left_idx in range(i - n, i):
                if candles[left_idx]["high"] - candidate_high > epsilon:
                    is_swing_high = False
                    break
            if is_swing_high:
                for right_idx in range(i + 1, i + n + 1):
                    if candles[right_idx]["high"] - candidate_high > epsilon:
                        is_swing_high = False
                        break
            
            # C. Evaluate Pure Swing Low Geometry Rules
            is_swing_low = True
            for left_idx in range(i - n, i):
                if candidate_low - candles[left_idx]["low"] > epsilon:
                    is_swing_low = False
                    break
            if is_swing_low:
                for right_idx in range(i + 1, i + n + 1):
                    if candidate_low - candles[right_idx]["low"] > epsilon:
                        is_swing_low = False
                        break

            # D. Execute Configurable Equal-Extrema Plateau Tie-Breaking Architecture
            if is_swing_high:
                # Check for equal highs within the lookback window envelope
                plateau_indices = [i]
                for idx in range(i - n, i + n + 1):
                    if idx != i and abs(candles[idx]["high"] - candidate_high) < epsilon:
                        plateau_indices.append(idx)
                
                if len(plateau_indices) > 1:
                    # Enforce priority checks: select target index by forward displacement velocity
                    best_idx = plateau_indices[0]
                    max_displacement = -1.0
                    
                    for p_idx in plateau_indices:
                        if p_idx + n < total_candles:
                            # Forward price drop vector magnitude calculation
                            forward_slice = candles[p_idx + 1 : p_idx + n + 1]
                            displacement = max([abs(c["high"] - candidate_high) for c in forward_slice]) if forward_slice else 0.0
                            if displacement > max_displacement:
                                max_displacement = displacement
                                best_idx = p_idx
                            elif abs(displacement - max_displacement) < epsilon:
                                # Volume breaker implementation layer
                                if candles[p_idx]["volume"] > candles[best_idx]["volume"]:
                                    best_idx = p_idx
                    if i != best_idx:
                        is_swing_high = False

            if is_swing_low:
                plateau_indices = [i]
                for idx in range(i - n, i + n + 1):
                    if idx != i and abs(candles[idx]["low"] - candidate_low) < epsilon:
                        plateau_indices.append(idx)
                
                if len(plateau_indices) > 1:
                    best_idx = plateau_indices[0]
                    max_displacement = -1.0
                    
                    for p_idx in plateau_indices:
                        if p_idx + n < total_candles:
                            forward_slice = candles[p_idx + 1 : p_idx + n + 1]
                            displacement = max([abs(c["low"] - candidate_low) for c in forward_slice]) if forward_slice else 0.0
                            if displacement > max_displacement:
                                max_displacement = displacement
                                best_idx = p_idx
                            elif abs(displacement - max_displacement) < epsilon:
                                if candles[p_idx]["volume"] > candles[best_idx]["volume"]:
                                    best_idx = p_idx
                    if i != best_idx:
                        is_swing_low = False

            # E. Append Verified Records Matched to the Strict Fact Schema Definition
            if is_swing_high or is_swing_low:
                stype: Literal["HIGH", "LOW"] = "HIGH" if is_swing_high else "LOW"
                sprice = candidate_high if is_swing_high else candidate_low
                
                # Strict look-ahead protection: confirmation target is forced to index i+N close time
                confirmed_ts = candles[i + n]["timestamp"]
                unique_swing_id = f"{symbol.upper()}-{timeframe.upper()}-{stype}-{candidate_ts}"
                
                elapsed_ms = (time.perf_counter() - start_wall_clock) * 1000.0
                
                swing_facts.append({
                    "swing_id": unique_swing_id,
                    "job_id": job_id,
                    "timestamp": candidate_ts,
                    "swing_type": stype,
                    "price": sprice,
                    "index_position": i,
                    "confirmed_at_ts": confirmed_ts,
                    "status": "DISCOVERED",
                    "window_meta": {
                        "configured_n": n,
                        "left_window_actual": n,
                        "right_window_actual": n
                    },
                    "metrics": {
                        "engine_version": "v1.0-frozen-spec",
                        "processing_time_ms": elapsed_ms,
                        "dataset_hash_sha256": dataset_hash
                    }
                })

        return swing_facts
