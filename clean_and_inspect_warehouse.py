#!/usr/bin/env python3
# Core Data Validation Engine Focus: Precision Timestamp and Resolution Auditor

import os
import sys
import time
from utils.database import db_manager

print("==================================================================")
print("          APEX QUANT PLATFORM: PRECISION RECOVERY AUDITOR          ")
print("==================================================================")

DB_PATH = "market_data/warehouse/price_warehouse.db"

def run_precision_audit():
    if not os.path.exists(DB_PATH):
        print(f"❌ CRITICAL FAILURE: Database file not found at: {DB_PATH}")
        sys.exit(1)

    print("✅ File Found. Evaluating millisecond conversions and timeframe footprints...")

    with db_manager.price_db() as conn:
        # 1. Fetch data inventory grouped by symbol and timeframe
        query = """
            SELECT 
                symbol, 
                timeframe, 
                COUNT(*), 
                MIN(timestamp), 
                MAX(timestamp) 
            FROM crypto_candles 
            GROUP BY symbol, timeframe 
            ORDER BY symbol ASC, timeframe ASC;
        """
        records = conn.execute(query).fetchall()

        print("\n==================================================================")
        print("                REALIGNED WAREHOUSE INVENTORY REPORT              ")
        print("==================================================================")
        print(f" {'TICKER':<10} | {'TF':<5} | {'ROW COUNT':<12} | {'START DATE (UTC)':<17} | {'END DATE (UTC)':<17}")
        print("------------------------------------------------------------------")

        for row in records:
            symbol, tf, count, min_ts, max_ts = row
            
            # FIX: Convert millisecond timestamps to seconds for correct Python datetime translation
            start_seconds = min_ts / 1000.0 if min_ts > 50000000000 else min_ts
            end_seconds = max_ts / 1000.0 if max_ts > 50000000000 else max_ts
            
            start_date = time.strftime('%Y-%m-%d %H:%M', time.gmtime(start_seconds))
            end_date = time.strftime('%Y-%m-%d %H:%M', time.gmtime(end_seconds))
            
            print(f" {symbol:<10} | {tf:<5} | {count:<12,} | {start_date:<17} | {end_date:<17}")
        print("==================================================================")

        # 2. Forensic Resolution Check: Inspect the true time step inside the 1M data block
        print("\n-> Running forensic look into the '1M' timeframe data rows...")
        sample_query = """
            SELECT timestamp, open, close 
            FROM crypto_candles 
            WHERE timeframe = '1M' 
            ORDER BY timestamp ASC 
            LIMIT 3;
        """
        sample_rows = conn.execute(sample_query).fetchall()

        if len(sample_rows) >= 2:
            ts1 = sample_rows[0][0]
            ts2 = sample_rows[1][0]
            delta_seconds = (ts2 - ts1) / 1000.0
            print(f"   ├── Row 1 Timestamp : {ts1} ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(ts1/1000.0))})")
            print(f"   ├── Row 2 Timestamp : {ts2} ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(ts2/1000.0))})")
            print(f"   └── Mapped Step Delta: {delta_seconds:.0f} seconds")
            
            if delta_seconds == 60:
                print("\n🚨 FORENSIC VERDICT CONVERTED: The '1M' field contains 1-MINUTE DATA.")
                print("    Your database has been contaminated with micro-candles inside macro slots.")
            elif delta_seconds >= 2419200:
                print("\n✅ FORENSIC VERDICT CONVERTED: The '1M' field contains true Monthly data.")
        else:
            print("   └── Insufficient rows inside the 1M partition block to perform step metrics.")

if __name__ == "__main__":
    run_precision_audit()
