import sqlite3
import ccxt
import time
from datetime import datetime, timezone
import os

DB_PATH = "price_warehouse.db"
EXCHANGE = ccxt.binance({
    'enableRateLimit': True,
    'rateLimit': 1200  # Safe rate limit for Binance
})

ASSETS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
TIMEFRAMES = {'15m': '15M', '1h': '1H', '4h': '4H', '1d': '1D', '1w': '1W', '1M': '1M'}

# Target Start Date: Jan 1, 2021
START_TS = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

def init_db():
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
    # Add index for faster replay queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sym_tf_ts ON crypto_candles(symbol, timeframe, timestamp)")
    conn.commit()
    conn.close()

def get_latest_timestamp(symbol, timeframe):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM crypto_candles WHERE symbol=? AND timeframe=?", (symbol, timeframe))
    res = cursor.fetchone()[0]
    conn.close()
    return res if res else START_TS

def fetch_deep_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for symbol in ASSETS:
        db_symbol = symbol.replace("/", "")
        
        for ccxt_tf, db_tf in TIMEFRAMES.items():
            print(f"\n📥 Syncing {db_symbol} [{db_tf}]...")
            
            # Start from the latest candle we have, or 2021
            current_since = get_latest_timestamp(db_symbol, db_tf)
            total_fetched = 0
            
            while True:
                try:
                    ohlcv = EXCHANGE.fetch_ohlcv(symbol, ccxt_tf, since=current_since, limit=1000)
                    
                    if not ohlcv or len(ohlcv) <= 1:
                        print(f"   └── ✅ {db_symbol} {db_tf} is up to date.")
                        break
                        
                    records = []
                    for row in ohlcv:
                        ts = int(row[0])
                        records.append((db_symbol, db_tf, ts, row[1], row[2], row[3], row[4], row[5]))
                    
                    cursor.executemany("""
                        INSERT OR IGNORE INTO crypto_candles 
                        (symbol, timeframe, timestamp, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, records)
                    conn.commit()
                    
                    total_fetched += len(records)
                    current_since = int(ohlcv[-1][0]) # Advance the timestamp for the next page
                    
                    print(f"   ├── Fetched page: {len(records)} candles (Total: {total_fetched})")
                    time.sleep(EXCHANGE.rateLimit / 1000.0) # Respect rate limit
                    
                except Exception as e:
                    print(f"❌ Error fetching {symbol} {db_tf}: {e}")
                    time.sleep(5) # Back off on error
                    break
                    
    conn.close()

if __name__ == "__main__":
    init_db()
    fetch_deep_history()
