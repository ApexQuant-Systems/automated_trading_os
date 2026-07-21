# Component Manifest Contract Header
__module_name__ = "production_data_quality_auditor"
__build_version__ = "1.6.1-stable"
__spec_contract_hash__ = "0x106_production_auditor_v2"

import time
from typing import Dict, Any, List, Tuple
from utils.database import db_manager
from market_data.asset_registry import asset_registry

class DataQualityAuditor:
    """Institutional-grade time-series data validator enforcing geometric and chronological constraints."""

    def __init__(self, allow_gaps: bool = False, enforce_strict_ohlc: bool = True):
        self.allow_gaps = allow_gaps
        self.enforce_strict_ohlc = enforce_strict_ohlc
        # Timeframe mapping duration values calculated strictly in seconds
        self._expected_deltas = {
            "15M": 900, "1H": 3600, "4H": 14400, "1D": 86400, "1W": 604800, "1M": 2592000
        }

    def audit_loaded_dataset(self, symbol: str, timeframe: str, job_id: str) -> Tuple[float, bool]:
        """Scans partitioned price tables to perform comprehensive validation across data parameters."""
        asset_meta = asset_registry.get_asset(symbol)
        asset_class = asset_meta["asset_class"].lower()
        table_name = f"{asset_class}_candles"

        expected_delta = self._expected_deltas.get(timeframe.upper())
        if not expected_delta:
            return 100.0, True

        # Fetch all columns required for structural invariant checking
        with db_manager.price_db() as conn:
            cursor = conn.execute(
                f"SELECT timestamp, open, high, low, close, volume FROM {table_name} WHERE symbol = ? AND timeframe = ? AND job_id = ? ORDER BY timestamp ASC;",
                (symbol.upper(), timeframe.upper(), job_id)
            )
            rows = cursor.fetchall()

        if not rows:
            return 100.0, True

        total_rows = len(rows)
        critical_violations_triggered = 0
        missing_candles_accumulated = 0
        current_machine_time = int(time.time())
        
        anomalies_payload: List[Tuple] = []
        previous_ts = None

        for row in rows:
            ts = row["timestamp"]
            o = row["open"]
            h = row["high"]
            l = row["low"]
            c = row["close"]
            v = row["volume"]

            # lens 1: Presence & Complete Field Extraction Check
            if None in (ts, o, h, l, c, v):
                critical_violations_triggered += 1
                anomalies_payload.append((job_id, symbol, timeframe, ts, ts, 1, "CRITICAL_NULL_OMISSION"))
                continue

            # Lens 2: Geometric Candle Invariant Matrices Check
            if self.enforce_strict_ohlc:
                if h < o or h < c or l > o or l > c or h < l or v < 0:
                    critical_violations_triggered += 1
                    anomalies_payload.append((job_id, symbol, timeframe, ts, ts, 1, "CRITICAL_OHLC_INVERSION"))

            # Lens 3 & 4: Sequence Monotonicity and Duplication Checks
            if previous_ts is not None:
                if ts == previous_ts:
                    critical_violations_triggered += 1
                    anomalies_payload.append((job_id, symbol, timeframe, ts, ts, 1, "CRITICAL_DUPLICATE_TIMESTAMP"))
                elif ts < previous_ts:
                    critical_violations_triggered += 1
                    anomalies_payload.append((job_id, symbol, timeframe, ts, previous_ts, 1, "CRITICAL_SEQUENCE_INVERSION"))
                elif ts - previous_ts > expected_delta:
                    # Lens 5: Chronological Expected Interval Step Check
                    skipped_bars = int((ts - previous_ts) / expected_delta) - 1
                    missing_candles_accumulated += skipped_bars
                    severity = "INFO" if skipped_bars <= 2 else ("WARNING" if skipped_bars <= 12 else "CRITICAL_GAP")
                    
                    if severity == "CRITICAL_GAP" or not self.allow_gaps:
                        critical_violations_triggered += 1
                        
                    anomalies_payload.append((job_id, symbol, timeframe, previous_ts + expected_delta, ts - expected_delta, skipped_bars, severity))

            previous_ts = ts

        # Direct streaming to the isolated audit dataspace table
        if anomalies_payload:
            with db_manager.audit_db() as conn:
                conn.executemany("""
                    INSERT INTO data_gap_logs (
                        job_id, symbol, timeframe, gap_start_timestamp, gap_end_timestamp, 
                        missing_candles_count, severity_level, detected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, [a + (current_machine_time,) for a in anomalies_payload])

        # Compute data score index parameters
        total_defects = critical_violations_triggered + missing_candles_accumulated
        if total_rows > 0:
            quality_score = max(0.0, round((1.0 - (total_defects / (total_rows + missing_candles_accumulated))) * 100, 2))
        else:
            quality_score = 100.0

        # Enforce strict zero-critical violation rule to pass circuit breaker constraints
        passes_validation_gate = (critical_violations_triggered == 0) and (quality_score >= 98.0)

        return quality_score, passes_validation_gate

data_quality_auditor = DataQualityAuditor(allow_gaps=False, enforce_strict_ohlc=True)
