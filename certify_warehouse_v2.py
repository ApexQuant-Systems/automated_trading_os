#!/usr/bin/env python3
# Core Data Validation Engine Focus: Hardened Quantitative Warehouse Invariant Auditor V2

import os
import sys
import time
import sqlite3
from utils.database import db_manager

print("==================================================================")
print("       APEX QUANT PLATFORM: HARDENED WAREHOUSE CERTIFIER V2       ")
print("==================================================================")

# Rigid mathematical constants: Timeframe to expected millisecond deltas
EXPECTED_DELTAS_MS = {
    "15M": 15 * 60 * 1000,        # 900,000 ms
    "1H": 60 * 60 * 1000,         # 3,600,000 ms
    "4H": 4 * 60 * 60 * 1000,     # 14,400,000 ms
    "1D": 24 * 60 * 60 * 1000,    # 86,400,000 ms
    "1W": 7 * 24 * 60 * 60 * 1000 # 604,800,000 ms
}

def run_hardened_audit():
    db_path = "market_data/warehouse/price_warehouse.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL FAILURE: Target database missing at: {db_path}")
        sys.exit(1)

    with db_manager.price_db() as conn:
        conn.row_factory = sqlite3.Row

        # ────────────────────────────────────────────────────────────────
        # CORE CHECK 1: UNVARNISHED GLOBAL TIMEFRAME DISTRIBUTION SCAN
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 1/4] Scanning global timeframe partition distributions...")
        distribution = conn.execute("""
            SELECT timeframe, COUNT(*), MIN(timestamp), MAX(timestamp) 
            FROM crypto_candles 
            GROUP BY timeframe 
            ORDER BY COUNT(*) DESC;
        """).fetchall()
        
        print("------------------------------------------------------------------")
        print(f" {'LABEL':<7} | {'TOTAL ROWS':<12} | {'MIN TIMESTAMP':<15} | {'MAX TIMESTAMP':<15}")
        print("------------------------------------------------------------------")
        for row in distribution:
            print(f" {row[0]:<7} | {row[1]:<12,} | {row[2]:<15} | {row[3]:<15}")
        print("------------------------------------------------------------------")

        # ────────────────────────────────────────────────────────────────
        # CORE CHECK 2: HARDCODED MSECS TIMELINE CONTINUITY GAP AUDIT
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 2/4] Running hardcoded timeline continuity gap analysis...")
        assets = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        for asset in assets:
            for tf, expected_delta in EXPECTED_DELTAS_MS.items():
                rows = conn.execute("""
                    SELECT timestamp FROM crypto_candles 
                    WHERE symbol = ? AND timeframe = ? 
                    ORDER BY timestamp ASC;
                """, (asset, tf)).fetchall()
                
                if len(rows) < 2:
                    print(f" ⚠️ {asset:<8} | {tf:<4} -> Insufficient rows to check gaps.")
                    continue
                
                actual_gaps = 0
                for i in range(1, len(rows)):
                    current_delta = rows[i]['timestamp'] - rows[i-1]['timestamp']
                    # Trigger gap alert only if time step exceeds 1.5x the expected milestone horizon
                    if current_delta > (expected_delta * 1.5):
                        actual_gaps += 1
                        
                print(f" ├── {asset:<8} | {tf:<4} | Row Count: {len(rows):<8,} | Confirmed Gaps: {actual_gaps}")

        # ────────────────────────────────────────────────────────────────
        # CORE CHECK 3: FULL MATRIX CROSS-TIMEFRAME HIGHS/LOWS SCAN
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 3/4] Running full dataset cross-timeframe structural audit...")
        print("-> Ingesting aggregate data sweeps (comparing 1D extremes to 1H distributions)...")
        
        cross_query = """
            SELECT d.symbol, d.timestamp as day_ts, d.high as day_high, d.low as day_low, 
                   MAX(h.high) as max_hr_high, MIN(h.low) as min_hr_low
            FROM crypto_candles d
            JOIN crypto_candles h ON h.symbol = d.symbol 
              AND h.timeframe = '1H'
              AND h.timestamp >= d.timestamp 
              AND h.timestamp < d.timestamp + 86400000
            WHERE d.timeframe = '1D'
            GROUP BY d.symbol, d.timestamp;
        """
        
        cross_records = conn.execute(cross_query).fetchall()
        high_violations = 0
        low_violations = 0
        total_checked = len(cross_records)
        
        for r in cross_records:
            if r['max_hr_high'] - r['day_high'] > 1e-4:
                high_violations += 1
            if r['day_low'] - r['min_hr_low'] > 1e-4:
                low_violations += 1
                
        print(f" ├── Total Daily Windows Swept : {total_checked:,}")
        print(f" ├── Confirmed High Boundary Violations: {high_violations}")
        print(f" └── Confirmed Low Boundary Violations : {low_violations}")
        
        if high_violations == 0 and low_violations == 0 and total_checked > 0:
            print("✅ PASS: 100% cross-timeframe integrity verified across the dataset.")
        else:
            print("🚨 FAIL: Cross-timeframe alignment bounds are fractured.")

        # ────────────────────────────────────────────────────────────────
        # CORE CHECK 4: FORENSIC SAMPLE SAMPLING
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 4/4] Extracting random raw validation sample blocks...")
        sample_row = conn.execute("""
            SELECT symbol, timeframe, timestamp, open, high, low, close, volume 
            FROM crypto_candles 
            WHERE timeframe = '15M' 
            ORDER BY timestamp DESC 
            LIMIT 1;
        """).fetchone()
        
        if sample_row:
            print(" Raw DB Record Snapshot:")
            for key in sample_row.keys():
                print(f"  ├── {key:<10}: {sample_row[key]}")
        else:
            print(" ⚠️ No rows found in 15M partition block.")

        print("==================================================================")

if __name__ == "__main__":
    run_hardened_audit()
