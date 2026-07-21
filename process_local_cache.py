#!/usr/bin/env python3
# Core Warehouse Processing Engine Focus: Complete Local Cache Ingestion

import os
import sys
import time
from utils.database import db_manager
from market_data.asset_registry import asset_registry
from market_data.transformer import canonical_transformer
from market_data.loader import warehouse_loader
from market_data.auditor import data_quality_auditor

print("==================================================================")
print("          APEX QUANT PLATFORM: BULK WAREHOUSE INGESTION CORE      ")
print("==================================================================")

db_manager.initialize_all_schemas()

# Realign asset parameters to match the true 2017 cache footprint on disk
CRYPTO_ASSETS = {
    "BTCUSDT": {"start_year": 2017, "start_month": 8},
    "ETHUSDT": {"start_year": 2017, "start_month": 8},
    "SOLUSDT": {"start_year": 2020, "start_month": 8}
}

EXPLICIT_TIMEFRAMES = ["15M", "1H", "4H", "1D", "1W", "1M"]
CURRENT_YEAR = 2026
CURRENT_MONTH = 6

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
print(f"──► Found {total_tasks} historical archives inside local workspace index maps.")
print("-> Initiating high-speed transactional parse and loading sequence...")

processed_count = 0
success_count = 0
failed_count = 0
start_time = time.time()

for task in tasks_to_process:
    processed_count += 1
    job_key = task["job_id"]
    symbol = task["symbol"]
    tf = task["timeframe"]
    path = task["file_path"]
    
    with db_manager.metadata_db() as conn:
        exists = conn.execute("SELECT 1 FROM dataset_manifests WHERE dataset_id = ?;", (job_key,)).fetchone()
    if exists:
        success_count += 1
        continue

    if not os.path.exists(path):
        failed_count += 1
        continue

    try:
        file_hash = canonical_transformer.calculate_file_sha256(path)
        candles = canonical_transformer.transform_binance_zip(path)
        
        if not candles:
            failed_count += 1
            print(f" [{processed_count}/{total_tasks}] ❌ Extraction Error: Empty rows inside {job_key}")
            continue

        rows_written = warehouse_loader.load_candles(symbol, "crypto", tf, job_key, candles)
        quality_score, passes_purity = data_quality_auditor.audit_loaded_dataset(symbol, tf, job_key)
        
        if not passes_purity:
            failed_count += 1
            print(f" [{processed_count}/{total_tasks}] ❌ Validation Drop: {job_key} Purity = {quality_score}")
            continue

        with db_manager.metadata_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dataset_manifests (
                    dataset_id, symbol, timeframe, venue, provider, start_timestamp, end_timestamp, 
                    total_rows, parser_version, warehouse_version, file_hash_sha256, download_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                job_key, symbol, tf, "BINANCE", "BINANCE_VISION",
                candles[0][0], candles[-1][0], rows_written, "1.1.0", "1.6.1",
                file_hash, "local.cache.ingest", int(time.time())
            ))
            
        success_count += 1
        sys.stdout.write(f"\r Processing Progress: [{success_count}/{total_tasks}] Complete ──► Loaded {symbol} {tf} ({rows_written} lines)")
        sys.stdout.flush()

    except Exception as process_exception:
        failed_count += 1
        print(f"\n [Exception] Execution failed on job block {job_key}: {str(process_exception)}")

elapsed_mins = (time.time() - start_time) / 60
print("\n------------------------------------------------------------------")
print("                WAREHOUSE PROCESSING COMPLETION SUMMARY           ")
print("------------------------------------------------------------------")
print(f" Ingestion Processing Duration    : {elapsed_mins:.2f} Minutes Total")
print(f" Datasets Verified RESEARCH_READY : {success_count} / {total_tasks}")
print(f" Corrupted / Malformed Task Drops : {failed_count}")
print("==================================================================\n")
