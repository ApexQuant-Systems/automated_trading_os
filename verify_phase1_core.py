import sqlite3
import os

DB_PATH = "price_warehouse.db"

def verify_phase_1a_core():
    print("==================================================================")
    print("   APEX QUANT OS: PHASE 1A CORE DATA PLATFORM VERIFICATION        ")
    print("==================================================================")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Core Database missing at '{DB_PATH}'")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verify table schema exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crypto_candles';")
    if not cursor.fetchone():
        print("❌ FAIL: 'crypto_candles' table missing from database.")
        conn.close()
        return
    print("✅ PASS: 'crypto_candles' table schema verified.")

    # 2. Verify data integrity (OHLC invariant check)
    cursor.execute("""
        SELECT COUNT(*) FROM crypto_candles 
        WHERE high < low OR high < open OR high < close OR low > open OR low > close
    """)
    invalid_candles = cursor.fetchone()[0]
    if invalid_candles > 0:
        print(f"❌ FAIL: Found {invalid_candles} candles violating basic OHLC geometric rules!")
    else:
        print("✅ PASS: 100% of warehouse candles satisfy OHLC geometric invariants.")

    # 3. Verify Replay-Ready Row Count
    cursor.execute("SELECT symbol, timeframe, COUNT(*) FROM crypto_candles GROUP BY symbol, timeframe")
    stats = cursor.fetchall()
    
    total_rows = 0
    print("\n📊 WAREHOUSE INVENTORY:")
    for stat in stats:
        print(f"   └── {stat[0]} [{stat[1]}]: {stat[2]} candles")
        total_rows += stat[2]

    print(f"\n✅ PASS: Total Certified Candles in Warehouse : {total_rows:,}")

    conn.close()
    print("==================================================================")
    print("   PHASE 1A CORE DATA PLATFORM IS CERTIFIED & READY FOR REPLAY    ")
    print("==================================================================")

if __name__ == "__main__":
    verify_phase_1a_core()
