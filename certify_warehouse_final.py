#!/usr/bin/env python3
# Core Data Validation Engine Focus: Final Certified Invariant Auditor (Pure Seconds Math)

import os
import sys
import time
import sqlite3
from utils.database import db_manager

print("==================================================================")
print("       APEX QUANT PLATFORM: FINAL WAREHOUSE CERTIFIER (SECONDS)   ")
print("==================================================================")

# Rigid mathematical constants: Timeframe to expected SECOND deltas
EXPECTED_DELTAS_SEC = {
    "15M": 15 * 60,               # 900 seconds
    "1H": 60 * 60,                # 3,600 seconds
    "4H": 4 * 60 * 60,            # 14,400 seconds
    "1D": 24 * 60 * 60,           # 86,400 seconds
    "1W": 7 * 24 * 60 * 60,       # 604,800 seconds
    "1M": 30 * 24 * 60 * 60       # Approximate monthly step baseline
}

def run_seconds_audit():
    db_path = "market_data/warehouse/price_warehouse.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL FAILURE: Target database missing at: {db_path}")
        sys.exit(1)

    with db_manager.price_db() as conn:
        conn.row_factory = sqlite3.Row

        # ────────────────────────────────────────────────────────────────
        # CHECK 1: TIMELINE TIMESTEP CONTINUITY GAP AUDIT (SECONDS)
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 1/3] Running pure second continuity gap analysis...")
        assets = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        tfs = ["15M", "1H", "4H", "1D", "1W"]
        
        for asset in assets:
            for tf in tfs:
                expected_delta = EXPECTED_DELTAS_SEC[tf]
                rows = conn.execute("""
                    SELECT timestamp FROM crypto_candles 
                    WHERE symbol = ? AND timeframe = ? 
                    ORDER BY timestamp ASC;
                """, (asset, tf)).fetchall()
                
                if len(rows) < 2:
                    continue
                
                actual_gaps = 0
                for i in range(1, len(rows)):
                    current_delta = rows[i]['timestamp'] - rows[i-1]['timestamp']
                    if current_delta > (expected_delta * 1.5):
                        actual_gaps += 1
                        
                print(f" ├── {asset:<8} | {tf:<4} | Rows: {len(rows):<8,} | Confirmed Gaps: {actual_gaps}")

        # ────────────────────────────────────────────────────────────────
        # CHECK 2: GLOBAL FULL MATRIX CROSS-TIMEFRAME ALIGNMENT AUDIT
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 2/3] Running full matrix cross-timeframe structural audit...")
        print("-> Comparing 1D extremes directly against 24-hour 1H windows...")
        
        cross_query = """
            SELECT d.symbol, d.timestamp as day_ts, d.high as day_high, d.low as day_low, 
                   MAX(h.high) as max_hr_high, MIN(h.low) as min_hr_low
            FROM crypto_candles d
            JOIN crypto_candles h ON h.symbol = d.symbol 
              AND h.timeframe = '1H'
              AND h.timestamp >= d.timestamp 
              AND h.timestamp < d.timestamp + 86400
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
                
        print(f" ├── Total Daily Windows Evaluated : {total_checked:,}")
        print(f" ├── Confirmed High Boundary Violations: {high_violations}")
        print(f" └── Confirmed Low Boundary Violations : {low_violations}")
        
        if high_violations == 0 and low_violations == 0 and total_checked > 0:
            print("✅ PASS: 100% cross-timeframe alignment bounds are completely verified.")
        else:
            print("🚨 FAIL: Data range drift verified inside database partitions.")

        # ────────────────────────────────────────────────────────────────
        # CHECK 3: VERIFY MONTHLY DISTRIBUTION INTEGRITY
        # ────────────────────────────────────────────────────────────────
        print("\n[CHECK 3/3] Verifying Monthly distribution integrity (True 1mo)...")
        for asset in assets:
            m_count = conn.execute("""
                SELECT COUNT(*) FROM crypto_candles WHERE symbol = ? AND timeframe = '1M';
            """, (asset,)).fetchone()[0]
            print(f" ├── {asset:<8} | 1M Total Stored Rows: {m_count}")

        print("==================================================================")

if __name__ == "__main__":
    run_seconds_audit()
