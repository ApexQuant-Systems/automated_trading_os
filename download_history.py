#!/usr/bin/env python3
# Core Data Ingestion Engine Focus: Sequential Diagnostic Ingestion Engine

import os
import sys
import time
import urllib.request
import ssl

print("==================================================================")
print("       APEX QUANT PLATFORM: DIAGNOSTIC INGESTION RUNTIME         ")
print("==================================================================")

# Frozen Tier 1 Crypto Baseline Targets
CRYPTO_ASSETS = {
    "BTCUSDT": {"start_year": 2017, "start_month": 8},
    "ETHUSDT": {"start_year": 2017, "start_month": 8},
    "SOLUSDT": {"start_year": 2020, "start_month": 8}
}

EXPLICIT_TIMEFRAMES = {
    "15M": "15m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
    "1W": "1w",
    "1M": "1mo"
}

# Explicitly cap boundaries at June 2026 (Last completed monthly block available)
CURRENT_YEAR = 2026
CURRENT_MONTH = 6

download_queue = []
total_evaluated = 0
already_exists_count = 0

print("-> Evaluating historical loop boundaries and cache state...")

for symbol, meta in CRYPTO_ASSETS.items():
    for tf_display, tf_folder in EXPLICIT_TIMEFRAMES.items():
        start_yr = meta["start_year"]
        
        for year in range(start_yr, CURRENT_YEAR + 1):
            start_mo = meta["start_month"] if year == start_yr else 1
            end_mo = CURRENT_MONTH if year == CURRENT_YEAR else 12
            
            for month in range(start_mo, end_mo + 1):
                total_evaluated += 1
                
                # Construct precise case-sensitive target string arrays
                url = f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/{tf_folder}/{symbol}-{tf_folder}-{year}-{month:02d}.zip"
                dest_file = f"{symbol}-{tf_display}-{year}-{month:02d}.zip"
                dest_path = f"market_data/raw/crypto/{symbol}/{tf_display.lower()}/{dest_file}"
                
                # Verbose diagnostic tracking for the first month of each timeframe array block
                if month == start_mo and year == start_yr:
                    print(f"  [Diagnostic Trace] {symbol} {tf_display} Loop Initialization:")
                    print(f"    ├── Target URL : {url}")
                    print(f"    ├── Local Path : {dest_path}")
                    print(f"    └── Disk Check : os.path.exists = {os.path.exists(dest_path)}")
                
                # Cache checking logic enforcement
                if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                    already_exists_count += 1
                    continue
                    
                download_queue.append({
                    "job_id": f"{symbol}-{tf_display}-{year}-{month:02d}",
                    "url": url,
                    "dest_path": dest_path
                })

print("------------------------------------------------------------------")
print("               QUEUE GENERATION DIAGNOSTIC SUMMARY                ")
print("------------------------------------------------------------------")
print(f" Total Chronological Combinations Checked : {total_evaluated}")
print(f" Valid Archive Files Detected on Disk     : {already_exists_count}")
print(f" Missing Blocks Enqueued for Execution    : {len(download_queue)}")
print("------------------------------------------------------------------\n")

if not download_queue:
    print("✓ Workspace Balanced: 100% of required historical blocks are already present on disk.")
    sys.exit(0)

# Execute the download queue sequentially to isolate failures one by one
success_count = 0
failed_count = 0
ctx = ssl._create_unverified_context()

print("Launching sequential network ingress loop...")
for index, task in enumerate(download_queue, 1):
    job_id = task["job_id"]
    url = task["url"]
    dest_path = task["dest_path"]
    
    print(f"[{index}/{len(download_queue)}] Ingesting Target: {job_id}")
    print(f"   ├── Fetch URL: {url}")
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 APEX Quant Ingestion'})
        with urllib.request.urlopen(req, timeout=15.0, context=ctx) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        print("   └── Status   : ✅ SUCCESS")
        success_count += 1
    except Exception as e:
        print(f"   └── Status   : ❌ FAILED | Reason: {str(e)}")
        failed_count += 1
        
        # Immediate diagnostic halt to inspect initial network blockages cleanly
        print("\n[HALT] Ingestion paused on first failure to isolate workspace variables.")
        sys.exit(1)

print("\n==================================================================")
print("              SEQUENTIAL ACQUISITION SPRINT COMPLETE              ")
print("==================================================================")
