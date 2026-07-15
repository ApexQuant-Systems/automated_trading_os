import os
import time
from data.csv_adapter import csv_adapter
from utils.database import db

print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR MODULE 1.2 ===")
start_time = time.perf_counter()

# 1. Generate local testing environment files dynamically
test_csv_path = "real_historical_ticks.csv"
with open(test_csv_path, "w", encoding="utf-8") as f:
    f.write("timestamp,open,high,low,close,volume\n")
    f.write("1721500000,60000.0,61000.0,59500.0,60500.0,450.0\n")
    f.write("1721586400,60500.0,62000.0,60100.0,61800.0,520.0\n")
    f.write("1721672800,61800.0,61500.0,61000.0,61200.0,300.0\n")  # Bad candle: High < Open (Will be filtered)
    f.write("1721759200,61200.0,61900.0,60800.0,61500.0,-50.0\n")  # Bad candle: Negative Volume (Will be filtered)

# 2. Execute chunked ingestion streaming pipeline metrics
metrics = csv_adapter.load_csv_in_chunks(test_csv_path, "BTCUSD", "1H", chunk_size=2)
duration_ms = (time.perf_counter() - start_time) * 1000

print("\n-------------------------------------------")
print(f"Metrics Output:  Attempted: {metrics['attempted']} | Inserted: {metrics['inserted']} | Rejected: {metrics['rejected']}")
print(f"Runtime Tracking: {duration_ms:.2f} ms")
print("-------------------------------------------")

# 3. Dynamic Assertions Checks
test_failed = False

if metrics["attempted"] != 4 or metrics["inserted"] != 2 or metrics["rejected"] != 2:
    print("❌ Assertion Failure: Ingress filter count metrics mismatched.")
    test_failed = True
else:
    print("✓ Verification: Out-of-sample data filtering rules working accurately.")

with db.connection() as conn:
    row = conn.execute("SELECT * FROM market_data WHERE symbol = 'BTCUSD' ORDER BY timestamp DESC LIMIT 1").fetchone()
    if row and row["close"] == 61800.0:
        print(f"✓ Verification: Disk data retrievability loop working correctly. Read close price: ${row['close']}")
    else:
        print("❌ Assertion Failure: Target database records mismatch or not found.")
        test_failed = True

# Clean disk footprints
if os.path.exists(test_csv_path):
    os.remove(test_csv_path)

if test_failed:
    print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
    exit(1)
else:
    print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
    exit(0)