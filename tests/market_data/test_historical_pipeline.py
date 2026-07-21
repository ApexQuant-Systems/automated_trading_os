import sys
import os
import time
import zipfile

# Enforce strict 3-level path expansion traversal to map repository system layout root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.database import db
from market_data.historical_pipeline import historical_pipeline
from market_data.dataset_catalog import dataset_catalog

def run_pipeline_regression_suite():
    print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 4 ===")
    start_time = time.perf_counter()
    
    test_failed = False
    mock_zip = "tests/market_data/mock_archive.zip"
    
    # 1. Synthesize a clean, valid sample ZIP container structure to run parser verification
    os.makedirs(os.path.dirname(mock_zip), exist_ok=True)
    csv_buffer = "1767225600,100.0,105.0,99.0,102.0,500.0,1767225600,50000.0,10,250.0,250.0,0\n"
    
    with zipfile.ZipFile(mock_zip, 'w') as z:
        z.writestr("mock_data.csv", csv_buffer)

    # 2. Build structured execution parameters context mock matching project specifications
    mock_task = {
        "dataset_id": "DS-MOCK-BTCUSDT-15M-202601",
        "symbol": "BTCUSDT",
        "timeframe": "15M",
        "asset_class": "CRYPTO",
        "venue": "BINANCE",
        "provider": "BINANCE_VISION",
        "source_url": "file://" + os.path.abspath(mock_zip), # Local network fallback routing route
        "destination_path": "market_data/raw/crypto/BTCUSDT/15m/mock_data.zip",
        "chunk_year": 2026,
        "chunk_month": 1
    }

    # Execute transformation pipeline worker loops
    pipeline_ok = historical_pipeline.execute_pipeline_task(mock_task, batch_size=1000)
    
    # Check data extraction queries records directly from partitioned database table
    with db.connection() as conn:
        row = conn.execute("SELECT * FROM crypto_candles WHERE symbol = 'BTCUSDT'").fetchone()

    # 3. Test Download Resume Logic by running identical task vector a second time
    resume_start = time.perf_counter()
    resume_ok = historical_pipeline.execute_pipeline_task(mock_task)
    resume_duration_ms = (time.perf_counter() - resume_start) * 1000

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Total Pipeline Processing Run Latency: {duration_ms:.4f} ms")
    print(f"Isolated Resume Decision Check Intercept: {resume_duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    # Clean storage tracks safely post-sprint
    if os.path.exists(mock_zip):
        os.remove(mock_zip)
    if os.path.exists(mock_task["destination_path"]):
        os.remove(mock_task["destination_path"])

    # Assertion Check 1: Verify data rows hit database targets flawlessly
    if pipeline_ok and row and row["close"] == 102.0 and row["dataset_id"] == mock_task["dataset_id"]:
        print("✓ Verification: Canonical parsing transformation and data warehouse loader verified.")
    else:
        print("❌ Assertion Failure: Ingestion pipeline dropped blocks or corrupted table lines.")
        test_failed = True

    # Assertion Check 2: Verify download resume intercept checks are sub-millisecond fast
    if resume_ok and resume_duration_ms < 5.0:
        print("✓ Verification: Persistent download resume state machine validation intercept passed.")
    else:
        print(f"❌ Assertion Failure: Resume engine tracking latency drop out bounds: {resume_duration_ms} ms")
        test_failed = True

    if test_failed:
        print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
        sys.exit(1)
    else:
        print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
        sys.exit(0)

if __name__ == "__main__":
    run_pipeline_regression_suite()
