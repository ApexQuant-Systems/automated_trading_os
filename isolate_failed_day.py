#!/usr/bin/env python3
# Core Data Validation Engine Focus: Forensic Single-Day Mismatch Analyzer

import os
import sys
import time
import sqlite3
from utils.database import db_manager

print("==================================================================")
print("        APEX QUANT PLATFORM: SINGLE-DAY FORENSIC ANALYZER         ")
print("==================================================================")

def run_forensic_analysis():
    db_path = "market_data/warehouse/price_warehouse.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL FAILURE: Database file missing at: {db_path}")
        sys.exit(1)

    with db_manager.price_db() as conn:
        conn.row_factory = sqlite3.Row

        # 1. Locate the first explicit daily candle that breaks alignment invariants
        query = """
            SELECT d.symbol, d.timestamp as day_ts, d.open as day_open, d.high as day_high, 
                   d.low as day_low, d.close as day_close,
                   MAX(h.high) as max_hr_high, MIN(h.low) as min_hr_low
            FROM crypto_candles d
            JOIN crypto_candles h ON h.symbol = d.symbol 
              AND h.timeframe = '1H'
              AND h.timestamp >= d.timestamp 
              AND h.timestamp < d.timestamp + 86400000
            WHERE d.timeframe = '1D'
            GROUP BY d.symbol, d.timestamp
            HAVING abs(MAX(h.high) - d.high) > 1e-4 
               OR abs(d.low - MIN(h.low)) > 1e-4
            ORDER BY d.timestamp ASC
            LIMIT 1;
        """
        
        faulty_day = conn.execute(query).fetchone()
        
        if not faulty_day:
            print("✅ STRANGE: No failed days found using this strict query constraint.")
            return
            
        symbol = faulty_day['symbol']
        day_ts = faulty_day['day_ts']
        day_str = time.strftime('%Y-%m-%d', time.gmtime(day_ts / 1000.0))
        
        print(f"🚨 TARGET FRACTURE FOUND: {symbol} on {day_str} (Raw Ts: {day_ts})")
        print("------------------------------------------------------------------")
        print(" MASTER DAILY CANDLE RECORD (1D Slot):")
        print(f"  ├── Open  : {faulty_day['day_open']}")
        print(f"  ├── High  : {faulty_day['day_high']}  <───[ EXPECTED MAX ]")
        print(f"  ├── Low   : {faulty_day['day_low']}  <───[ EXPECTED MIN ]")
        print(f"  └── Close : {faulty_day['day_close']}")
        print("------------------------------------------------------------------")
        print(" CALCULATED HOURLY AGGREGATES FROM JOIN WINDOW:")
        print(f"  ├── Max Hourly High Detected: {faulty_day['max_hr_high']}")
        print(f"  └── Min Hourly Low Detected : {faulty_day['min_hr_low']}")
        print("------------------------------------------------------------------")
        
        # 2. Extract all 24 individual hourly candles allocated to this specific window
        print(f" Extracting all 1H sub-candles inside window [{day_ts} to {day_ts + 86400000}]:")
        
        hourly_candles = conn.execute("""
            SELECT timestamp, open, high, low, close, volume 
            FROM crypto_candles 
            WHERE symbol = ? AND timeframe = '1H'
              AND timestamp >= ? AND timestamp < ?
            ORDER BY timestamp ASC;
        """, (symbol, day_ts, day_ts + 86400000)).fetchall()
        
        print(f" {'HOURLY TIMESTAMP':<16} | {'TIME (UTC)':<12} | {'OPEN':<10} | {'HIGH':<10} | {'LOW':<10} | {'CLOSE':<10}")
        print("--------------------------------------------------------------------------------")
        
        for hr in hourly_candles:
            hr_ts = hr['timestamp']
            hr_str = time.strftime('%H:%M:%S', time.gmtime(hr_ts / 1000.0))
            print(f" {hr_ts:<16} | {hr_str:<12} | {hr['open']:<10} | {hr['high']:<10} | {hr['low']:<10} | {hr['close']:<10}")
            
        print("--------------------------------------------------------------------------------")
        print(f" Total Hourly Candles Found in Window: {len(hourly_candles)} / 24")
        print("==================================================================")

if __name__ == "__main__":
    run_forensic_analysis()
