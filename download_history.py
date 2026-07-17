#!/usr/bin/env python3
# Component Manifest Contract Header
__module_name__ = "data_platform_orchestration_gateway"
__build_version__ = "1.3.0-production"

import sys
import os
import time

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.asset_registry import asset_registry
from market_data.planner import download_planner
from market_data.scheduler import job_scheduler
from market_data.downloader import historical_downloader
from market_data.transformer import canonical_transformer
from market_data.loader import warehouse_loader
from utils.database import db_manager

def run_data_collection_loop(target_asset_class: str = None, max_jobs_to_process: int = 3):
    print("==================================================================")
    print("            APEX QUANT DATA PLATFORM CORE COMMAND RUNTIME         ")
    print("==================================================================")
    
    # 1. Verify and initialize the database tables structure
    print("-> Verifying multi-dataspace database partitions layout maps...")
    db_manager.initialize_all_schemas()
    
    # 2. Synchronize the system download matrix configurations list
    print("-> Synchronizing target grid allocations universe metrics...")
    full_job_list = download_planner.generate_job_matrix()
    new_jobs_seeded = job_scheduler.enqueue_job_matrix(full_job_list)
    
    # Extract structural baseline state matrix integers directly from metadata tables
    with db_manager.metadata_db() as conn:
        total_grid = conn.execute("SELECT COUNT(*) as count FROM job_scheduler;").fetchone()["count"]
        total_ready = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'RESEARCH_READY';").fetchone()["count"]
        total_failed = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'FAILED';").fetchone()["count"]

    print(f"  Inventory State: Total Mapped Chunks: {total_grid} | Ready: {total_ready} | Failed: {total_failed}")
    print("------------------------------------------------------------------")
    filter_msg = f"Targeting Category: {target_asset_class.upper()}" if target_asset_class else "Targeting Universe: ALL"
    print(f"Launching active collection worker loop ({filter_msg} | Limit: {max_jobs_to_process} runs)")
    print("------------------------------------------------------------------")

    processed_count = 0
    
    # 3. Process records down the persistent database queue timeline loop
    while processed_count < max_jobs_to_process:
        # Fetch the next eligible task from the persistent queue database table
        active_job = None
        with db_manager.metadata_db() as conn:
            if target_asset_class:
                query = """
                    SELECT j.* FROM job_scheduler j
                    JOIN asset_registry a ON j.symbol = a.symbol
                    WHERE j.status IN ('PENDING', 'DOWNLOADED') AND j.retries < 3 AND a.asset_class = ?
                    ORDER BY j.chunk_year ASC, j.chunk_month ASC LIMIT 1;
                """
                row = conn.execute(query, (target_asset_class.upper(),)).fetchone()
            else:
                query = """
                    SELECT * FROM job_scheduler 
                    WHERE status IN ('PENDING', 'DOWNLOADED') AND retries < 3 
                    ORDER BY chunk_year ASC, chunk_month ASC LIMIT 1;
                """
                row = conn.execute(query).fetchone()
                
            if row:
                active_job = dict(row)
                if active_job["status"] == "PENDING":
                    conn.execute("UPDATE job_scheduler SET status = 'DOWNLOADING', started_at = ? WHERE job_id = ?;", 
                                 (int(time.time()), active_job["job_id"]))

        if not active_job:
            print("✓ Ingestion Queue Clear: Zero pending download tasks match current query constraints.")
            break
            
        job_key = active_job["job_id"]
        symbol = active_job["symbol"]
        tf = active_job["timeframe"]
        
        asset_meta = asset_registry.get_asset(symbol)
        file_name = f"{symbol}-{tf}-{active_job['chunk_year']}-{active_job['chunk_month']:02d}.zip"
        dest_path = f"market_data/raw/{asset_meta['asset_class'].lower()}/{symbol}/{tf.lower()}/{file_name}"
        
        print(f"[{processed_count + 1}/{max_jobs_to_process}] Processing Task: {job_key} (Current State: {active_job['status']})")
        
        # A. Execute Download step if the task is still marked PENDING
        download_success = True
        if active_job["status"] == "PENDING":
            download_success = historical_downloader.download_job_chunk(active_job)
            if download_success:
                job_scheduler.update_job_status(job_key, "DOWNLOADED")
            else:
                print(f"  └─ Network Failure: Task execution dropped loops.")
                job_scheduler.increment_retry_counter(job_key, "Network transfer timeout or file missing.")
                processed_count += 1
                print("------------------------------------------------------------------")
                continue

        # B. Execute Validation and Transformation steps
        print("  └─ Running file integrity validation checks and parsing operations...")
        file_hash = canonical_transformer.calculate_file_sha256(dest_path)
        candles = canonical_transformer.transform_binance_zip(dest_path)
        
        if not candles:
            print(f"  └─ Extraction Failure: Malformed zip structure or empty CSV rows inside {file_name}")
            job_scheduler.update_job_status(job_key, "FAILED", error_msg="Data conversion extraction failure.")
            processed_count += 1
            print("------------------------------------------------------------------")
            continue
            
        print(f"  └─ Verification Clear: Calculated SHA256 Hash = {file_hash[:16]}... | Found Rows: {len(candles)}")

        # C. Stream verified records to the partitioned database warehouse
        print("  └─ Streaming canonical matrices to relational storage partitions...")
        rows_committed = warehouse_loader.load_crypto_candles(symbol, tf, job_key, candles)
        
        # D. Write data manifest updates and advance task state to RESEARCH_READY
        with db_manager.metadata_db() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO dataset_manifests (
                    dataset_id, symbol, timeframe, venue, provider, start_timestamp, end_timestamp, 
                    total_rows, parser_version, warehouse_version, file_hash_sha256, download_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                job_key, symbol, tf, asset_meta["venue"], asset_meta["provider"],
                candles[0][0], candles[-1][0], rows_committed, "1.0.0", "1.5.0",
                file_hash, "data.binance.vision", int(time.time())
            ))
            
        job_scheduler.update_job_status(job_key, "RESEARCH_READY")
        print(f"  └─ Transaction Finalized: Mapped {rows_committed} records. State upgraded to: RESEARCH_READY")
            
        processed_count += 1
        print("------------------------------------------------------------------")

    # Fetch post-run execution telemetry metrics summaries
    with db_manager.metadata_db() as conn:
        final_pending = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'PENDING';").fetchone()["count"]
        final_ready = conn.execute("SELECT COUNT(*) as count FROM job_scheduler WHERE status = 'RESEARCH_READY';").fetchone()["count"]
    
    print("                      RUNNING SPRINT PROCESS RECORD               ")
    print("------------------------------------------------------------------")
    print(f" Current Pending Queue Tasks Balance : {final_pending}")
    print(f" Total Completed Warehouse Datasets  : {final_ready}")
    print("==================================================================\n")

if __name__ == "__main__":
    # Process the active downloaded files through the transformation pipeline
    run_data_collection_loop(target_asset_class=None, max_jobs_to_process=4)
