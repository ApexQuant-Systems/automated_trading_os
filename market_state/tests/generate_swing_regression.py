import sqlite3
import json
import os
from market_state.models.candle import Candle
from market_state.analysis.swings import SwingDetector

DB_PATH = "price_warehouse.db"
OUTPUT_PATH = "market_state/tests/regression/btc_4h_swings_ref.json"

def generate_regression_snapshot():
    if not os.path.exists(DB_PATH):
        print("❌ ERROR: price_warehouse.db not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load 500 fixed historical 4H BTC candles
    cursor.execute("""
        SELECT timestamp, open, high, low, close, volume 
        FROM crypto_candles 
        WHERE symbol='BTCUSDT' AND timeframe='4H' 
        ORDER BY timestamp ASC 
        LIMIT 500
    """)
    rows = cursor.fetchall()
    conn.close()

    raw_candles = [{"timestamp": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]} for r in rows]
    candles = [Candle(**c) for c in raw_candles]

    swings = SwingDetector.detect(candles, window=2)

    snapshot_data = [
        {"timestamp": s.timestamp, "price": s.price, "type": s.type}
        for s in swings
    ]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(snapshot_data, f, indent=2)

    print(f"✅ LEVEL 5 REGRESSION SNAPSHOT CREATED!")
    print(f"📁 Saved {len(snapshot_data)} reference swings to '{OUTPUT_PATH}'")

if __name__ == "__main__":
    generate_regression_snapshot()
