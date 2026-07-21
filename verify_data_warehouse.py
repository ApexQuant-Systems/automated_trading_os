import sqlite3
import os

DB_PATH = "market_data/warehouse/price_warehouse.db"

def verify_warehouse():
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Warehouse database not found at '{DB_PATH}'")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==================================================================")
    print("        APEX QUANT OS: PHASE 1 DATA WAREHOUSE INTEGRITY AUDIT     ")
    print("==================================================================")

    # 1. Row counts and timestamp coverage per asset & timeframe
    print("\n[CHECK 1/3] Database Table Inventory & Timeframe Coverage:")
    print(f"{'SYMBOL':<10} | {'TIMEFRAME':<8} | {'ROW COUNT':<12} | {'MIN TS (UNIX)':<12} | {'MAX TS (UNIX)':<12}")
    print("-" * 65)

    assets = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    timeframes = ["15M", "1H", "4H", "1D", "1W", "1M"]

    for symbol in assets:
        for tf in timeframes:
            cursor.execute(
                "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM crypto_candles WHERE symbol=? AND timeframe=?",
                (symbol, tf)
            )
            count, min_ts, max_ts = cursor.fetchone()
            count_str = f"{count:,}" if count else "0"
            min_str = str(min_ts) if min_ts else "N/A"
            max_str = str(max_ts) if max_ts else "N/A"
            print(f"{symbol:<10} | {tf:<8} | {count_str:<12} | {min_str:<12} | {max_str:<12}")

    # 2. Check for duplicate timestamps
    print("\n[CHECK 2/3] Checking for Duplicate Timestamps...")
    cursor.execute("""
        SELECT symbol, timeframe, timestamp, COUNT(*) 
        FROM crypto_candles 
        GROUP BY symbol, timeframe, timestamp 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"❌ FAIL: Found {len(duplicates)} duplicate timestamp entries!")
        for d in duplicates[:5]:
            print(f"   └── Duplicate: {d}")
    else:
        print("✅ PASS: 0 duplicate timestamps found across all assets & timeframes.")

    # 3. Cross-Timeframe Alignment Check (1D vs 24x 1H sub-candles)
    print("\n[CHECK 3/3] Cross-Timeframe High/Low Boundary Check (1D vs 1H)...")
    cursor.execute("""
        SELECT d.symbol, d.timestamp, d.high, d.low, 
               MAX(h.high) as max_1h_high, MIN(h.low) as min_1h_low
        FROM crypto_candles d
        JOIN crypto_candles h ON h.symbol = d.symbol 
          AND h.timeframe = '1H'
          AND h.timestamp >= d.timestamp 
          AND h.timestamp < d.timestamp + 86400
        WHERE d.timeframe = '1D'
        GROUP BY d.symbol, d.timestamp
    """)
    rows = cursor.fetchall()
    high_violations = 0
    low_violations = 0
    total_days = len(rows)

    for r in rows:
        sym, ts, day_high, day_low, max_1h_high, min_1h_low = r
        if max_1h_high and (max_1h_high - day_high > 1e-4):
            high_violations += 1
        if min_1h_low and (day_low - min_1h_low > 1e-4):
            low_violations += 1

    print(f" ├── Total Daily Windows Evaluated : {total_days:,}")
    print(f" ├── High Boundary Violations       : {high_violations}")
    print(f" └── Low Boundary Violations        : {low_violations}")

    if high_violations == 0 and low_violations == 0 and total_days > 0:
        print("✅ PASS: 100% Cross-timeframe boundaries are verified.")
    else:
        print(f"⚠️ NOTICE: {high_violations + low_violations} boundary violations detected.")

    print("==================================================================")
    conn.close()

if __name__ == "__main__":
    verify_warehouse()
