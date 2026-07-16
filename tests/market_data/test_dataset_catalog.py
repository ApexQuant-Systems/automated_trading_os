import sys
import os
import time

# Enforce explicit 3-level traversal to lock onto the repository root directory boundary
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_data.dataset_catalog import DatasetCatalog

def run_catalog_regression_checks():
    print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 3 ===")
    start_time = time.perf_counter()
    
    sandbox_db = "market_data/warehouse/sandbox_metadata.db"
    if os.path.exists(sandbox_db):
        os.remove(sandbox_db)

    catalog_engine = DatasetCatalog(db_path=sandbox_db)
    test_failed = False

    # 1. Test registration functionality pass
    ds_id = "DS-ETHUSDT-1H-202601"
    reg_ok = catalog_engine.register_dataset(ds_id, "ETHUSDT", "1H", 1767225600, 1769817600)
    
    if reg_ok and catalog_engine.get_dataset_status(ds_id) == "REGISTERED":
        print("✓ Verification: Dataset structural catalog initialization registration passed.")
    else:
        print("❌ Assertion Failure: Catalog failed to record initial tracking vector state.")
        test_failed = True

    # 2. Test lifecycle state transitions logic checks
    update_ok = catalog_engine.update_dataset_status(ds_id, "VALIDATED")
    if update_ok and catalog_engine.get_dataset_status(ds_id) == "VALIDATED":
        print("✓ Verification: State machine engine tracking status transition passed.")
    else:
        print("❌ Assertion Failure: State update failed or tracking parameters corrupted.")
        test_failed = True

    # 3. Test parameter constraints logic drops for illegal inputs
    bad_update = catalog_engine.update_dataset_status(ds_id, "ILLEGAL_STATE_TOKEN")
    if not bad_update and catalog_engine.get_dataset_status(ds_id) == "VALIDATED":
        print("✓ Verification: Catalog safety boundary filter successfully blocked corrupt state input.")
    else:
        print("❌ Assertion Failure: System permitted illegal lifecycle state mutation injections.")
        test_failed = True

    # Cleanup sandbox files cleanly
    if os.path.exists(sandbox_db):
        os.remove(sandbox_db)

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Catalog Ingestion State Latency: {duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    if test_failed:
        print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
        sys.exit(1)
    else:
        print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
        sys.exit(0)

if __name__ == "__main__":
    run_catalog_regression_checks()
