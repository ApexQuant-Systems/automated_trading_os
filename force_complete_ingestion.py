#!/usr/bin/env python3
# Core Data Recovery Engine Focus: Finalize 100% Warehouse Ingestion

import os
import sys
import time
from utils.database import db_manager
from market_data.transformer import canonical_transformer
from market_data.loader import warehouse_loader
from market_data.auditor import data_quality_auditor

print("==================================================================")
print("          APEX QUANT PLATFORM: WAREHOUSE COMPLETION CORE          ")
print("==================================================================")

# Initialize database structures
db_manager.initialize_all_schemas()

CRYPTO_ASSETS = {
    "BTCUSDT": {"start_year": 2017, "start_month": 8},
    "ETHUSDT": {"start_year": 2017, "start_month": 8},
    "SOLUSDT": {"start_year": 2020, "start_month": 8}
}

EXPLICIT_TIMEFRAMES = ["15M", "1H", "4H", "1D", "1W", "1M"]
CURRENT_YEAR = 2026
CURRENT_MONTH = 6

# 1. Reconstruct the entire 1,710 file execution grid
tasks_to_process = []
for symbol, meta in CRYPTO_ASSETS.items():
    for tf in EXPLICIT_TIMEFRAMES:
        start_yr = meta["start_year"]
        for year in range(start_yr, CURRENT_YEAR + 1):
            start_mo = meta["start_month"] if year == start_yr else 1
            end_mo = CURRENT_MONTH if year == CURRENT_YEAR else 12
            
            for month in range(start_mo, end_mo + 1):
                job_id = f"{symbol}-{tf}-{year}-{month:02d}"
                dest_file = f"{symbol}-{tf}-{year}-{month:02d}.zip"
                dest_path = f"market_data/raw/crypto/{symbol}/{tf.lower()}/{dest_file}"
                
                tasks_to_process.append({
                    "job_id": job_id,
                    "symbol": symbol,
                    "timeframe": tf,
                    "file_path": dest_path
                })

total_tasks = len(tasks_to_process)
print(f"──► Mapped Ingestion Grid: {total_tasks} Total Expected Block Archives.")

# 2. Check current manifest state to skip already loaded datasets
with db_manager.metadata_db() as conn:
    existing_manifests = {row[0] for row in conn.execute("SELECT dataset_id FROM dataset_manifests;").fetchall()}

print(f"🔒 Mapped {len(existing_manifests)} datasets already verified inside database manifests.")

processed_count = 0
success_count = len(existing_manifests)
failed_count = 0
start_time = time.time()

# 3. Process remaining data blocks transactionally
for task in tasks_to_process:
    processed_count += 1
    job_key = task["job_id"]
    symbol = task["symbol"]
    tf = task["timeframe"]
    path = task["file_path"]
    
    # Skip if already marked active and verified
    if job_key in existing_manifests:
        continue

    if not os.path.exists(path):
        failed_count += 1
        continue

    try:
        file_hash = canonical_transformer.calculate_file_sha256(path)
        candles = canonical_transformer.transform_binance_zip(path)
        
        if not candles:
            failed_count += 1
            print(f"\n❌ [{processed_count}/{total_tasks}] Empty CSV Error inside: {job_key}")
            continue

        # Dynamic attribute routing check to guarantee compatibility
        if hasattr(warehouse_loader, 'load_candles'):
            rows_written = warehouse_loader.load_candles(symbol, "crypto", tf, job_key, candles)
        else:
            rows_written = warehouse_loader.load_crypto_candles(symbol, tf, job_key, candles)
            
        # Secure the manifest token upgrade
        with db_manager.metadata_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dataset_manifests (
                    dataset_id, symbol, timeframe, venue, provider, start_timestamp, end_timestamp, 
                    total_rows, parser_version, warehouse_version, file_hash_sha256, download_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                job_key, symbol, tf, "BINANCE", "BINANCE_VISION",
                candles[0][0], candles[-1][0], rows_written, "1.1.0", "1.6.2",
                file_hash, "local.cache.ingest", int(time.time())
            ))
            
        success_count += 1
        sys.stdout.write(f"\r Ingesting Workspace Track: [{success_count}/{total_tasks}] Complete ──► Populated {job_key}")
        sys.stdout.flush()

    except Exception as e:
        failed_count += 1
        print(f"\n❌ System Exception on data target {job_key}: {str(e)}")

elapsed_mins = (time.time() - start_time) / 60
print("\n------------------------------------------------------------------")
print("                WAREHOUSE INGESTION CLOSURE SUMMARY               ")
print("------------------------------------------------------------------")
print(f" Completion Ingestion Velocity   : {elapsed_mins:.2f} Minutes Total")
print(f" Total Confirmed RESEARCH_READY   : {success_count} / {total_tasks}")
print(f" Skips, Drops, or Missing Blocks : {failed_count}")
print("==================================================================\n")
