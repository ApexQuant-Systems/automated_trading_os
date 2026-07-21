import sqlite3
import os

class ReplayLoader:
    """
    The strict API abstraction layer for historical market data.
    Downstream modules (Market State, Strategy) consume THIS, never raw SQL.
    """
    
    # Path relative to the project root
    DB_PATH = "price_warehouse.db"

    @classmethod
    def get_history(cls, symbol: str, timeframe: str, limit: int = None, start_ts: int = None, end_ts: int = None) -> list[dict]:
        """
        Retrieves historical OHLCV candles securely and deterministically.
        Returns a list of dictionaries ready for parsing by downstream object models.
        """
        if not os.path.exists(cls.DB_PATH):
            raise FileNotFoundError(f"Warehouse database not found at {cls.DB_PATH}")

        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        query = "SELECT timestamp, open, high, low, close, volume FROM crypto_candles WHERE symbol=? AND timeframe=?"
        params = [symbol, timeframe]

        if start_ts is not None:
            query += " AND timestamp >= ?"
            params.append(start_ts)
        
        if end_ts is not None:
            query += " AND timestamp <= ?"
            params.append(end_ts)

        query += " ORDER BY timestamp ASC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        # Translate raw tuples into standardized dictionary format
        return [
            {
                "timestamp": r[0],
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5])
            }
            for r in rows
        ]
