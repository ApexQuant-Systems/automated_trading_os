import time
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.database import RelationalPersistenceManager

print("\n=== RUNNING QUANT ENGINEERING REVIEW FOR PHASE 0 MODULE 0.3 ===")
start_time = time.perf_counter()

sandbox_db_path = "data/storage/sandbox_warehouse.db"
if os.path.exists(sandbox_db_path):
    os.remove(sandbox_db_path)

sandbox_db = RelationalPersistenceManager(db_path=sandbox_db_path)
test_failed = False

try:
    current_ts = int(time.time())
    
    with sandbox_db.connection() as conn:
        # Test Data Insertion 1: Ingestion metadata candlestick verification
        conn.execute("""
            INSERT INTO market_data (symbol, timeframe, timestamp, open, high, low, close, volume, spread, provider, exchange, timezone, ingestion_time, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("XAUUSD", "1H", 1782216000, 2350.0, 2365.0, 2345.0, 2360.0, 12000.0, 0.35, "REST_API", "VANTAGE", "UTC", current_ts, 99.8))

        # Test Data Insertion 2: Decoupled normalized feature store records insertion
        conn.execute("""
            INSERT INTO feature_store (symbol, timeframe, timestamp, feature_type, feature_key, feature_value)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("XAUUSD", "1H", 1782216000, "structure", "trend_state", "BULLISH"))

        # Test Data Insertion 3: Advanced telemetry performance journal verification
        conn.execute("""
            INSERT INTO trade_journal (trade_id, strategy_id, setup_score, entry_timestamp, exit_timestamp, symbol, timeframe, direction, entry_price, stop_loss, take_profit, risk_amount, position_size, spread, slippage, commission, swap, expected_rr, actual_rr, realized_pnl, execution_latency, exit_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("T-2026-001", "STRAT_S3_HYBRID", 85.5, 1782216000, 1782223200, "XAUUSD", "1H", "BUY", 2360.0, 2355.0, 2380.0, 10.0, 2.0, 0.35, 0.05, 2.0, 0.0, 4.0, 4.0, 40.0, 42.25, "TAKE_PROFIT_HIT"))

    # Pull records out to confirm exact schema parameters alignment
    with sandbox_db.connection() as conn:
        row_candle = conn.execute("SELECT * FROM market_data WHERE symbol = ?", ("XAUUSD",)).fetchone()
        row_feature = conn.execute("SELECT * FROM feature_store WHERE feature_type = ?", ("structure",)).fetchone()
        row_version = conn.execute("SELECT * FROM schema_version WHERE version = 1").fetchone()

    duration_ms = (time.perf_counter() - start_time) * 1000
    print("------------------------------------------------------------------")
    print(f"Decoupled DB Read-Write Loop Latency: {duration_ms:.4f} ms")
    print("------------------------------------------------------------------")

    if row_version and row_version["version"] == 1:
        print("✓ Verification: Schema versioning records tracker operational on baseline startup.")
    else:
        print("❌ Assertion Failure: Database migrations schema info dropped.")
        test_failed = True

    if row_candle and row_candle["exchange"] == "VANTAGE" and row_candle["quality_score"] == 99.8:
        print("✓ Verification: Ingestion telemetry tracking data fields confirmed inside data warehouse.")
    else:
        print("❌ Assertion Failure: Candlestick metadata parameter slots dropped mapping.")
        test_failed = True

    if row_feature and row_feature["feature_value"] == "BULLISH":
        print("✓ Verification: Normalized feature_store metrics time-series structure operational.")
    else:
        print("❌ Assertion Failure: Feature cache storage loops dropped metrics elements.")
        test_failed = True

except Exception as err:
    print(f"❌ Structural Exception Block Intercepted: {str(err)}")
    test_failed = True

finally:
    if os.path.exists(sandbox_db_path):
        os.remove(sandbox_db_path)

if test_failed:
    print("=== QUANT ENGINEERING STATUS: FAILED ===\n")
    exit(1)
else:
    print("=== QUANT ENGINEERING STATUS: PRODUCTION PASSED ===\n")
    exit(0)
