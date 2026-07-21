import sqlite3
import ccxt
import time
import os

DB_PATH = "price_warehouse.db"
EXCHANGE = ccxt.binance({'enableRateLimit': True})

ASSETS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
# Binance timeframe strings mapping to our system strings
TIMEFRAMES = {
    '15m': '15M',
    '1h': '1H',
    '4h': '4H',
    '1d': '1D',
    '1w': '1W',
    '1M': '1M'
}

def init_db():
    """Creates the SQLite database and table if it doesn't exist."""
    print(f"Initializing database at {os.path.abspath(DB_PATH)}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_candles (
            symbol TEXT,
            timeframe TEXT,
            timestamp INTEGER,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY (symbol, timeframe, timestamp)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database schema initialized.")

def fetch_and_store_data():
    """Fetches historical data and stores it in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for symbol in ASSETS:
        db_symbol = symbol.replace("/", "")  # 'BTC/USDT' -> 'BTCUSDT'
        
        for ccxt_tf, db_tf in TIMEFRAMES.items():
            print(f"📥 Fetching {db_symbol} [{db_tf}]...")
            
            # Fetch recent 1000 candles
            try:
                ohlcv = EXCHANGE.fetch_ohlcv(symbol, ccxt_tf, limit=1000)
                
                records = []
                for row in ohlcv:
                    timestamp = int(row[0])  # Unix timestamp in milliseconds
                    open_p, high_p, low_p, close_p, volume = row[1], row[2], row[3], row[4], row[5]
                    records.append((db_symbol, db_tf, timestamp, open_p, high_p, low_p, close_p, volume))
                
                # Insert ignoring duplicates
                cursor.executemany("""
                    INSERT OR IGNORE INTO crypto_candles 
                    (symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, records)
                
                conn.commit()
                print(f"   └── Saved {len(records)} rows.")
                
            except Exception as e:
                print(f"❌ Error fetching {symbol} {db_tf}: {e}")
                
            time.sleep(1) # Respect exchange rate limits

    conn.close()
    print("\n✅ All data downloaded and saved to price_warehouse.db!")

if __name__ == "__main__":
    init_db()
    fetch_and_store_data()
