import time
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.database import db
from data.historical_loader import historical_loader

print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 1 MODULE 1.1 ===")
start_time = time.perf_counter()

# Generate a continuous 10-candle history array containing a data-purity exception at index 5
mock_historical_payload = []
base_timestamp = 1770000000

for i in range(10):
    ts = base_timestamp + (i * 3600)
    if i == 5:
        # Malformed anomaly candle (High is lower than Low) to test the database firewall
        mock_historical_payload.append({
            "timestamp": ts, "open": 100.0, "high": 90.0, "low": 110.0, "close": 95.0, "volume": 500.0, "spread": 0.2
        })
    else:
        mock_historical_payload.append({
            "timestamp": ts, "open": 100.0 + i, "high": 105.0 + i, "low": 98.0 + i, "close": 102.0 + i, "volume": 1000.0, "spread": 0.1
        })

# Target execution pass using a sandbox database table instance configuration
result = historical_loader.load_and_seed_history(
    symbol="EURUSD",
    timeframe="1H",
    candle_data=mock_historical_payload,
    exchange="VANTAGE"
)

# Run Query Verification
with db.connection() as conn:
    total_rows = conn.execute("SELECT COUNT(*) as cnt FROM market_data WHERE symbol = 'EURUSD'").fetchone()["cnt"]
    corrupt_check = conn.execute("SELECT COUNT(*) as cnt FROM market_data WHERE high < low").fetchone()["cnt"]

duration_ms = (time.perf_counter() - start_time) * 1000
print("------------------------------------------------------------------")
print(f"Warehouse Ingestion Throughput Latency: {duration_ms:.4f} ms")
print("------------------------------------------------------------------")

test_failed = False

# Assertion Check 1: Verify data filter correctly dropped the corrupt candle record
if total_rows == 9:
    print("✓ Verification: Data Purity Firewall dropped malformed candle structure successfully.")
else:
    print(f"❌ Assertion Failure: Database allowed corrupt row penetration. Row Count: {total_rows}")
    test_failed = True

# Assertion Check 2: Confirm 0 corrupt database records exist inside the infrastructure storage
if corrupt_check == 0:
    print("✓ Verification: Zero structural data corruption anomalies detected inside market_data.")
else:
    print("❌ Assertion Failure: Corrupt storage index constraints tracking errors found.")
    test_failed = True

if test_failed:
    print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
    exit(1)
else:
    print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
    exit(0)
