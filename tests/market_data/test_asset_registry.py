import sys
import os
import time

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.asset_registry import asset_registry

def run_regression_checks():
    print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 1 ===")
    start_time = time.perf_counter()
    
    test_failed = False
    
    # Check 1: Verify full flattening load count totals exactly 15 assets
    total_assets = asset_registry.get_complete_watchlist()
    if len(total_assets) == 15:
        print("✓ Verification: Full asset universe volume loaded exactly to target bounds (15 instruments).")
    else:
        print(f"❌ Assertion Failure: Asset count metrics drifted out of bounds: {len(total_assets)}")
        test_failed = True

    # Check 2: Verify structural data parameters integrity for Crypto Tier
    try:
        btc_cfg = asset_registry.get_asset("BTCUSDT")
        if btc_cfg["venue"] == "BINANCE" and btc_cfg["price_precision"] == 2:
            print("✓ Verification: Tier 1 Crypto precision boundaries verified successfully.")
        else:
            print("❌ Assertion Failure: Crypto mapping profiles corrupted.")
            test_failed = True
    except Exception as e:
        print(f"❌ Check Failure: Raised mapping configuration lookup error: {str(e)}")
        test_failed = True

    # Check 3: Verify classification sorting logic maps for Forex Majors
    fx_list = asset_registry.get_watchlist_by_class("FOREX")
    if len(fx_list) == 5 and "EURUSD" in fx_list and "USDCAD" in fx_list:
        print("✓ Verification: Tier 2 Forex currency classification array sorted without loss.")
    else:
        print(f"❌ Assertion Failure: Category isolation filtering returned altered metrics: {fx_list}")
        test_failed = True

    # Check 4: Enforce error handling boundary validation checks
    if not asset_registry.verify_asset_exists("INVALID_TICKER"):
        print("✓ Verification: Safety validation filter caught unknown foreign asset requests safely.")
    else:
        print("❌ Assertion Failure: Unknown asset passed structural boundary constraints checks.")
        test_failed = True

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Registry Lookup Execution Latency: {duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    if test_failed:
        print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
        sys.exit(1)
    else:
        print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
        sys.exit(0)

if __name__ == "__main__":
    run_regression_checks()
