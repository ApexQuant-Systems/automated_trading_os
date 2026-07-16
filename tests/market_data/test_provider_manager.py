import sys
import os
import time

# Traverse exactly three levels up to resolve the true repository root directory boundary
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.provider_manager import provider_manager

def run_provider_regression_suite():
    print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 2 ===")
    start_time = time.perf_counter()
    
    test_failed = False

    # Define validation limits: 6-month tracking window segment across 2025
    start_ts = 1735689600  # 2025-01-01 00:00:00 UTC
    end_ts = 1751328000    # 2025-07-01 00:00:00 UTC

    # 1. Evaluate crypto mapping parameters configuration extraction
    try:
        crypto_tasks = provider_manager.generate_download_tasks("BTCUSDT", "15M", start_ts, end_ts)
        
        # Checking time segment array footprint sizes (Jan to Jul = 7 structural blocks)
        if len(crypto_tasks) == 7:
            print("✓ Verification: Historical month-by-month timeline task slicing math verified successfully.")
        else:
            print(f"❌ Assertion Failure: Timeline chunk generator mismatch: {len(crypto_tasks)}")
            test_failed = True

        first_task = crypto_tasks[0]
        expected_url = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/15m/BTCUSDT-15m-2025-01.zip"
        if first_task["source_url"] == expected_url and first_task["compression_type"] == "ZIP":
            print("✓ Verification: Binance Vision URL template mapping string generation verified.")
        else:
            print(f"❌ Assertion Failure: Remote endpoint string mismatch: {first_task['source_url']}")
            test_failed = True
            
        if "market_data/raw/crypto/BTCUSDT/15m/" in first_task["destination_path"]:
            print("✓ Verification: Partitioned raw physical data directory destination path validated.")
        else:
            print(f"❌ Assertion Failure: Target path layout formatting configuration corrupted: {first_task['destination_path']}")
            test_failed = True

    except Exception as err:
        print(f"❌ Check Failure: Crypto dataset planning raised errors: {str(err)}")
        test_failed = True

    # 2. Evaluate asset validation boundary constraints logic drops
    try:
        provider_manager.generate_download_tasks("INVALID_ASSET", "1H", start_ts, end_ts)
        print("❌ Assertion Failure: System allowed task compilation loop vectors for unregistered assets.")
        test_failed = True
    except KeyError:
        print("✓ Verification: Core protection filters blocked tasks routing for alien asset parameters.")

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Provider Tasks Resolution Latency: {duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    if test_failed:
        print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
        sys.exit(1)
    else:
        print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
        sys.exit(0)

if __name__ == "__main__":
    run_provider_regression_suite()
