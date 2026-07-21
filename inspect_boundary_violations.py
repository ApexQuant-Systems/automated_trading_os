import sqlite3
import os

DB_PATH = "price_warehouse.db"

def inspect_violations():
    if not os.path.exists(DB_PATH):
        if os.path.exists("market_data/warehouse/price_warehouse.db"):
            db_path = "market_data/warehouse/price_warehouse.db"
        else:
            print(f"❌ ERROR: Cannot find database file.")
            return
    else:
        db_path = DB_PATH

    print("==================================================================")
    print("   APEX QUANT OS: INVESTIGATING 2 DAILY BOUNDARY VIOLATIONS       ")
    print("==================================================================")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query daily candles and compare their High against the MAX(high) of 24 hourly sub-candles
    cursor.execute("""
        SELECT d.symbol, d.timestamp, d.open, d.high, d.low, d.close,
               MAX(h.high) as max_1h_high, MIN(h.low) as min_1h_low, COUNT(h.timestamp) as hourly_count
        FROM crypto_candles d
        JOIN crypto_candles h ON h.symbol = d.symbol 
          AND h.timeframe = '1H'
          AND h.timestamp >= d.timestamp 
          AND h.timestamp < d.timestamp + 86400
        WHERE d.timeframe = '1D'
        GROUP BY d.symbol, d.timestamp
        HAVING max_1h_high > d.high OR min_1h_low < d.low
    """)
    
    violations = cursor.fetchall()
    
    if not violations:
        print("✅ PASS: Zero boundary violations detected! (The previous query window issue is resolved).")
    else:
        print(f"⚠️ FOUND {len(violations)} BOUNDARY VIOLATION(S):\n")
        for v in violations:
            sym, ts, d_open, d_high, d_low, d_close, max_1h, min_1h, h_count = v
            print(f"📍 SYMBOL: {sym} | Daily Timestamp (UTC): {ts}")
            print(f"   ├── Daily High      : {d_high}")
            print(f"   ├── Max 1H High     : {max_1h} (Diff: +{max_1h - d_high:.4f})")
            print(f"   ├── Daily Low       : {d_low}")
            print(f"   ├── Min 1H Low      : {min_1h} (Diff: -{d_low - min_1h:.4f})")
            print(f"   └── Hourly Sub-Bars : {h_count} / 24 candles found in window")
            print("-" * 65)

    conn.close()

if __name__ == "__main__":
    inspect_violations()
