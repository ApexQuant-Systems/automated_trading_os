import sqlite3
import os
import matplotlib.pyplot as plt
from market_state.models.candle import Candle
from market_state.analysis.swings import SwingDetector

DB_PATH = "price_warehouse.db"

def generate_visual_overlay():
    if not os.path.exists(DB_PATH):
        if os.path.exists("market_data/warehouse/price_warehouse.db"):
            db_path = "market_data/warehouse/price_warehouse.db"
        else:
            print("❌ ERROR: Database file not found.")
            return
    else:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load 150 real 4H BTC candles for a clean visual chart
    cursor.execute("""
        SELECT timestamp, open, high, low, close, volume 
        FROM crypto_candles 
        WHERE symbol='BTCUSDT' AND timeframe='4H' 
        ORDER BY timestamp ASC 
        LIMIT 150
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ No data found.")
        return

    # Convert to Candle objects
    raw_candles = [
        {"timestamp": r[0], "open": r[1], "high": r[2], "low": r[3], "close": r[4], "volume": r[5]}
        for r in rows
    ]
    candles = [Candle(**c) for c in raw_candles]

    # Detect Swings (Window = 2)
    swings = SwingDetector.detect(candles, window=2)

    # Prepare data for plotting
    timestamps = [c.timestamp for c in candles]
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]

    plt.figure(figsize=(14, 7))

    # Plot Price Highs/Lows as range lines
    plt.plot(range(len(candles)), closes, label="BTC/USDT 4H Close", color="gray", alpha=0.6, linewidth=1.5)

    # Plot High/Low wicks range
    for idx in range(len(candles)):
        plt.vlines(idx, lows[idx], highs[idx], color="black" if closes[idx] >= candles[idx].open else "red", alpha=0.5)

    # Overlay Detected Swing Highs (Red Down-Triangles)
    swing_high_indices = []
    swing_high_prices = []
    for s in swings:
        if s.type == "HIGH":
            # Match timestamp to candle index
            for idx, c in enumerate(candles):
                if c.timestamp == s.timestamp:
                    swing_high_indices.append(idx)
                    swing_high_prices.append(s.price)
                    break

    # Overlay Detected Swing Lows (Green Up-Triangles)
    swing_low_indices = []
    swing_low_prices = []
    for s in swings:
        if s.type == "LOW":
            for idx, c in enumerate(candles):
                if c.timestamp == s.timestamp:
                    swing_low_indices.append(idx)
                    swing_low_prices.append(s.price)
                    break

    plt.scatter(swing_high_indices, swing_high_prices, color="red", marker="v", s=100, label="Swing High Peak", zorder=5)
    plt.scatter(swing_low_indices, swing_low_prices, color="green", marker="^", s=100, label="Swing Low Trough", zorder=5)

    plt.title("APEX QUANT OS: Level 4 Visual Validation — BTC/USDT 4H Swings", fontsize=14, fontweight="bold")
    plt.xlabel("Candle Index", fontsize=12)
    plt.ylabel("Price (USDT)", fontsize=12)
    plt.legend(loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.5)

    output_image = "swing_validation_btc_4h.png"
    plt.savefig(output_image, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"✅ LEVEL 4 VISUAL OVERLAY GENERATED SUCCESSFULLY!")
    print(f"🖼️ Chart saved to disk as: '{output_image}'")
    print(f"📊 Total Candles Plotted: {len(candles)} | Swing Highs: {len(swing_high_prices)} | Swing Lows: {len(swing_low_prices)}")

if __name__ == "__main__":
    generate_visual_overlay()
