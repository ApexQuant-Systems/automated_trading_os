#!/usr/bin/env python3
# Core Data Validation Engine Focus: Pre-Ingestion Archive Smoke Tester

import os
import sys
import zipfile
import csv
import io
import random
from typing import List, Tuple

print("==================================================================")
print("          APEX QUANT PLATFORM: ARCHIVE INTEGRITY SMOKE TEST       ")
print("==================================================================")

BASE_DIR = "market_data/raw/crypto"

def run_smoke_test() -> bool:
    if not os.path.exists(BASE_DIR):
        print(f"❌ Error: Core storage path [{BASE_DIR}] does not exist.")
        return False

    # 1. Discover all active zip blocks on disk
    all_zip_paths = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.zip'):
                all_zip_paths.append(os.path.join(root, file))

    if not all_zip_paths:
        print("❌ Error: Zero .zip files detected inside the repository directory tree.")
        return False

    print(f"-> Discovered {len(all_zip_paths)} filesystem records. Selecting random validation targets...")
    
    # Sample up to 5 distinct files to execute multi-horizon cross-sectional checking
    sample_size = min(5, len(all_zip_paths))
    test_samples = random.sample(all_zip_paths, sample_size)
    
    validation_failures = 0

    for idx, path in enumerate(test_samples, 1):
        print(f"\n[{idx}/{sample_size}] Checking Target Asset: {os.path.basename(path)}")
        print(f"   ├── File Location: {path}")
        
        # Test 1: Zip file binary structure and CRC validation
        if not zipfile.is_zipfile(path):
            print("   └── Status: ❌ CRITICAL FAILURE (Malformed zip header binary contract)")
            validation_failures += 1
            continue
            
        try:
            with zipfile.ZipFile(path, 'r') as archive:
                # Runs CRC32 checksum loops across internal files internally
                corrupt_file = archive.testzip()
                if corrupt_file:
                    print(f"   └── Status: ❌ CRITICAL FAILURE (CRC32 checksum mismatch on {corrupt_file})")
                    validation_failures += 1
                    continue
                
                # Test 2: Internal CSV allocation verification
                csv_files = [f for f in archive.namelist() if f.endswith('.csv')]
                if not csv_files:
                    print("   └── Status: ❌ CRITICAL FAILURE (No underlying .csv record inside archive envelope)")
                    validation_failures += 1
                    continue
                    
                with archive.open(csv_files[0]) as f:
                    text_layer = io.TextIOWrapper(f, encoding='utf-8')
                    csv_reader = csv.reader(text_layer)
                    
                    rows_parsed = 0
                    previous_ts = None
                    geometric_faults = 0
                    
                    for row in csv_reader:
                        if not row or row[0].isalpha():
                            continue
                            
                        rows_parsed += 1
                        try:
                            # Test 3: Type definitions and mathematical integrity boundaries
                            ts = int(row[0])
                            open_p = float(row[1])
                            high_p = float(row[2])
                            low_p  = float(row[3])
                            close_p = float(row[4])
                            volume = float(row[5])
                            
                            # Test 4: Chronological sequence constraint matching
                            if previous_ts is not None and ts <= previous_ts:
                                geometric_faults += 1
                            
                            # Test 5: Geometric high/low validation bounds
                            if high_p < open_p or high_p < close_p or low_p > open_p or low_p > close_p or high_p < low_p:
                                geometric_faults += 1
                                
                            previous_ts = ts
                        except (ValueError, IndexError):
                            geometric_faults += 1
                            
                    if rows_parsed == 0:
                        print("   └── Status: ❌ CRITICAL FAILURE (CSV parsed successfully but contained 0 rows)")
                        validation_failures += 1
                    elif geometric_faults > 0:
                        print(f"   └── Status: ❌ CRITICAL FAILURE ({geometric_faults} structural formatting variations logged)")
                        validation_failures += 1
                    else:
                        print(f"   └── Status: ✅ PASSED (Rows: {rows_parsed} | Chronology: Monotonic | Schema: Intact)")
                        
        except Exception as e:
            print(f"   └── Status: ❌ SYSTEM EXCEPTION ({str(e)})")
            validation_failures += 1

    print("\n------------------------------------------------------------------")
    print("                ARCHIVE INTEGRITY VERIFICATION REPORT             ")
    print("------------------------------------------------------------------")
    print(f" Total Samples Tested             : {sample_size}")
    print(f" Total Structural Corruptions Found: {validation_failures}")
    print("------------------------------------------------------------------")
    
    return validation_failures == 0

if __name__ == "__main__":
    suite_passed = run_smoke_test()
    if not suite_passed:
        print("❌ Smoke Test failed. Aborting database processing paths to shield system purity.")
        sys.exit(1)
    print("✓ Verification gateway clear. Data sets are safe to stream to warehouse loaders.")
    sys.exit(0)
