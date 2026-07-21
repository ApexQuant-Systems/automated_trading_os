import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = "price_warehouse.db"

def certify_warehouse():
    print("==================================================================")
    print("   APEX QUANT OS: PHASE 1A INSTITUTIONAL DATA AUDIT               ")
    print("==================================================================")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Database not found at '{DB_PATH}'")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    checks_passed = True

    # --- CHECK 1: NULL VALUES ---
    cursor.execute("""
        SELECT COUNT(*) FROM crypto_candles 
        WHERE open IS NULL OR high IS NULL OR low IS NULL OR close IS NULL OR volume IS NULL
    """)
    null_count = cursor.fetchone()[0]
    if null_count > 0:
        print(f"❌ [FAIL] Found {null_count} rows with NULL values.")
        checks_passed = False
    else:
        print("✅ [PASS] Zero NULL values detected.")

    # --- CHECK 2: NEGATIVE VOLUMES ---
    cursor.execute("SELECT COUNT(*) FROM crypto_candles WHERE volume < 0")
    neg_vol = cursor.fetchone()[0]
    if neg_vol > 0:
        print(f"❌ [FAIL] Found {neg_vol} rows with negative volume.")
        checks_passed = False
    else:
        print("✅ [PASS] Zero negative volume anomalies.")

    # --- CHECK 3: GEOMETRIC INVARIANTS ---
    cursor.execute("""
        SELECT COUNT(*) FROM crypto_candles 
        WHERE high < low OR high < open OR high < close OR low > open OR low > close
    """)
    geom_fails = cursor.fetchone()[0]
    if geom_fails > 0:
        print(f"❌ [FAIL] Found {geom_fails} geometric OHLC violations.")
        checks_passed = False
    else:
        print("✅ [PASS] 100% OHLC geometric integrity confirmed.")

    # --- CHECK 4: DUPLICATE TIMESTAMPS ---
    cursor.execute("""
        SELECT symbol, timeframe, timestamp, COUNT(*) 
        FROM crypto_candles 
        GROUP BY symbol, timeframe, timestamp 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"❌ [FAIL] Found {len(duplicates)} duplicate timestamps.")
        checks_passed = False
    else:
        print("✅ [PASS] Zero duplicate timestamps (Primary Key integrity upheld).")

    # --- CHECK 5: COVERAGE REPORT ---
    print("\n📊 WAREHOUSE COVERAGE & INVENTORY:")
    cursor.execute("""
        SELECT symbol, timeframe, COUNT(*), MIN(timestamp), MAX(timestamp) 
        FROM crypto_candles 
        GROUP BY symbol, timeframe
    """)
    stats = cursor.fetchall()
    
    total_rows = 0
    for stat in stats:
        sym, tf, count, min_ts, max_ts = stat
        total_rows += count
        min_dt = datetime.fromtimestamp(min_ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
        max_dt = datetime.fromtimestamp(max_ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d')
        print(f"   ├── {sym:<8} [{tf:>3}]: {count:>7,} candles | {min_dt} to {max_dt}")

    print("-" * 65)
    print(f"📈 TOTAL WAREHOUSE CANDLES: {total_rows:,}")

    print("\n==================================================================")
    if checks_passed:
        print("   ✅ PHASE 1A CORE DATA PLATFORM IS CERTIFIED SECURE")
    else:
        print("   ❌ PHASE 1A AUDIT FAILED. REPAIRS REQUIRED.")
    print("==================================================================")
    
    conn.close()

if __name__ == "__main__":
    certify_warehouse()
