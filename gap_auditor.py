import sqlite3

DB_PATH = "price_warehouse.db"

# Expected milliseconds between candles
TF_DELTAS = {
    '15M': 15 * 60 * 1000,
    '1H': 60 * 60 * 1000,
    '4H': 4 * 60 * 60 * 1000,
    '1D': 24 * 60 * 60 * 1000,
    '1W': 7 * 24 * 60 * 60 * 1000,
}

def audit_gaps():
    print("==================================================================")
    print("   APEX QUANT OS: PHASE 1A GAP & CONTINUITY AUDITOR               ")
    print("==================================================================")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    
    total_gaps = 0

    for symbol in assets:
        for tf, expected_delta in TF_DELTAS.items():
            cursor.execute(
                "SELECT timestamp FROM crypto_candles WHERE symbol=? AND timeframe=? ORDER BY timestamp ASC", 
                (symbol, tf)
            )
            rows = cursor.fetchall()
            
            if len(rows) < 2:
                continue
                
            gaps_found = 0
            for i in range(1, len(rows)):
                prev_ts = rows[i-1][0]
                curr_ts = rows[i][0]
                actual_delta = curr_ts - prev_ts
                
                if actual_delta != expected_delta:
                    gaps_found += 1
                    total_gaps += 1
            
            status = "✅ PASS" if gaps_found == 0 else f"⚠️ {gaps_found} GAPS DETECTED"
            print(f"{symbol:<10} | {tf:<4} | {status}")

    print("==================================================================")
    if total_gaps == 0:
        print("   ✅ 100% TEMPORAL CONTINUITY ACHIEVED.")
    else:
        print(f"   ⚠️ WARNING: {total_gaps} missing candles/gaps detected across DB.")
        print("   (Note: Some gaps are normal due to exchange maintenance).")
    print("==================================================================")
    conn.close()

if __name__ == "__main__":
    audit_gaps()
