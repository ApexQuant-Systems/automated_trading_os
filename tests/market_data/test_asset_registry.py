import sys
import os
import time

# Enforce explicit 3-level path expansion traversal to map repository root directory boundary
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.asset_registry import asset_registry

def run_persistent_registry_regression():
    print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 1 ===")
    start_time = time.perf_counter()
    
    test_failed = False
    
    # Check 1: Verify persistent lookup matching exactly 15 loaded assets
    watchlist = asset_registry.get_complete_watchlist()
    if len(watchlist) == 15:
        print("✓ Verification: Relational asset_registry table populated to target parameters bounds (15 instruments).")
    else:
        print(f"❌ Assertion Failure: Database record volumes drifted out of bounds: {len(watchlist)}")
        test_failed = True

    # Check 2: Verify structural data precision profile rows
    try:
        sol_meta = asset_registry.get_asset("SOLUSDT")
        if sol_meta["venue"] == "BINANCE" and sol_meta["volume_precision"] == 3:
            print("✓ Verification: Persistent storage layer decimal bounds mapped without row loss.")
        else:
            print("❌ Assertion Failure: Asset data row structural contents corrupted.")
            test_failed = True
    except Exception as err:
        print(f"❌ Check Failure: Relational mapping query generated exception tracker errors: {str(err)}")
        test_failed = True

    # Check 3: Verify asset class tracking array filter boundaries
    metals = asset_registry.get_watchlist_by_class("METALS")
    if len(metals) == 2 and "XAUUSD" in metals and "XAGUSD" in metals:
        print("✓ Verification: Partitioned classification lookups returning exact matches.")
    else:
        print(f"❌ Assertion Failure: Category parameters array extraction corrupted: {metals}")
        test_failed = True

    # Check 4: Assert relational validation firewall intercepts foreign tickers safely
    if not asset_registry.verify_asset_exists("UNKNOWN_INDEX"):
        print("✓ Verification: Persistent verification filter blocked untracked alien instrument calls.")
    else:
        print("❌ Assertion Failure: Operational database failed to isolate unknown ticker fields.")
        test_failed = True

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Persistent Registry Sweep Latency: {duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    if test_failed:
        print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
        sys.exit(1)
    else:
        print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
        sys.exit(0)

if __name__ == "__main__":
    run_persistent_registry_regression()
