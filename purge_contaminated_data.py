#!/usr/bin/env python3
# Core Data Recovery Engine Focus: Purge Contaminated 1M Table Records

import os
from utils.database import db_manager

print("==================================================================")
print("          APEX QUANT PLATFORM: WAREHOUSE PURGE KERNEL            ")
print("==================================================================")

with db_manager.price_db() as conn:
    print("-> Initiating deletion of contaminated '1M' price vectors...")
    cursor = conn.execute("DELETE FROM crypto_candles WHERE timeframe = '1M';")
    print(f"✅ Success: Purged {cursor.rowcount} contaminated rows from crypto_candles table.")
    
    print("-> Running database defragmentation (VACUUM)...")
    conn.execute("VACUUM;")
    print("✅ Success: Database storage space optimized.")

with db_manager.metadata_db() as conn:
    print("-> Purging broken metadata manifest logs...")
    cursor = conn.execute("DELETE FROM dataset_manifests WHERE timeframe = '1M';")
    print(f"✅ Success: Cleared {cursor.rowcount} stale manifest records.")

print("==================================================================")
print(" WAREHOUSE RESET COMPLETE: 1M Slots are clean. Ready for true 1mo data.")
print("==================================================================\n")
