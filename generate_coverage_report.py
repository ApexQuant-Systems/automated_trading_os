#!/usr/bin/env python3
# Core Data Validation Engine Focus: Empirical Warehouse Coverage Auditor

import os
import sys
import time
from utils.database import db_manager

print("==================================================================")
print("          APEX QUANT PLATFORM: DATA BASE COVERAGE AUDITOR          ")
print("==================================================================")

def run_warehouse_audit():
    # 1. Verify physical file allocations
    db_path = "market_data/warehouse/price_warehouse.db"
    if not os.path.exists(db_path):
        print(f"❌ CRITICAL FAILURE: Database file not found at expected path: {db_path}")
        sys.exit(1)
        
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"🔒 Database File Detected: {db_path} ({db_size_mb:.2f} MB)")

    # 2. Inspect underlying master schemas
    with db_manager.price_db() as conn:
        table_check = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='crypto_candles';"
        ).fetchone()
        
    if not table_check:
        print("❌ CRITICAL FAILURE: The required storage table 'crypto_candles' does not exist.")
        sys.exit(1)
        
    print("✅ Schema Contract Verified: 'crypto_candles' data structure is present.")
    print("-> Initiating complete stratified row count and boundary sweep...")

    # 3. Query stratified storage statistics grouped by ticker and horizon
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
    
    with db_manager.price_db() as conn:
        records = conn.execute(query).fetchall()

    if not records:
        print("\n⚠️ WARNING: The 'crypto_candles' table is completely empty. Zero rows returned.")
        print("==================================================================")
        return

    print("\n==================================================================")
    print("                PRODUCTION WAREHOUSE INVENTORY REPORT             ")
    print("==================================================================")
    print(f" {'TICKER':<10} | {'TF':<5} | {'TOTAL ROWS':<12} | {'EARLIEST RECORD (UTC)':<20} | {'LATEST RECORD (UTC)':<20}")
    print("--------------------------------------------------------------------------------------------------")

    for row in records:
        symbol = row[0]
        tf = row[1]
        row_count = row[2]
        min_ts = row[3]
        max_ts = row[4]
        
        # Convert unix seconds to human-readable text timestamps
        start_date = time.strftime('%Y-%m-%d %H:%M', time.gmtime(min_ts)) if min_ts else "N/A"
        end_date = time.strftime('%Y-%m-%d %H:%M', time.gmtime(max_ts)) if max_ts else "N/A"
        
        print(f" {symbol:<10} | {tf:<5} | {row_count:<12,} | {start_date:<20} | {end_date:<20}")

    print("==================================================================")
    
    # 4. Count total distinct data manifest logs to check pipeline tracking status
    with db_manager.metadata_db() as conn:
        manifest_count = conn.execute("SELECT COUNT(*) FROM dataset_manifests;").fetchone()[0]
    print(f" Total Datasets Marked 'RESEARCH_READY' in Manifests: {manifest_count} / 1710")
    print("==================================================================\n")

if __name__ == "__main__":
    run_warehouse_audit()
