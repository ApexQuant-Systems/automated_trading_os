# Component Manifest Contract Header
__module_name__ = "historical_market_replay_iterator"
__build_version__ = "4.5.0-stable"
__spec_contract_hash__ = "0x09_replay_iterator_core"
__regression_suite_hash__ = "0x09_replay_iterator_verify"

import sqlite3
from typing import Generator, Dict, Any
from utils.database import db
from logs.logger import logger

class HistoricalMarketReplayIterator:
    """Streams chronological market data from disk sequentially to eliminate look-ahead backtest bias."""

    def stream_market_history(self, symbol: str, timeframe: str, start_ts: int, end_ts: int, chunk_size: int = 2000) -> Generator[Dict[str, Any], None, None]:
        """Generates an iterative stream of candles ordered strictly by timestamp monotonicity."""
        logger.info(f"Initializing event-driven market replay sequence for {symbol} | [{start_ts} -> {end_ts}]")
        
        offset = 0
        while True:
            with db.connection() as conn:
                # Optimized chunked retrieval to balance disk read speeds with minimal memory consumption
                rows = conn.execute("""
                    SELECT timestamp, open, high, low, close, volume
                    FROM market_data
                    WHERE symbol = ? AND timeframe = ? AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                    LIMIT ? OFFSET ?
                """, (symbol, timeframe, start_ts, end_ts, chunk_size, offset)).fetchall()

            if not rows:
                break

            for row in rows:
                yield {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": row["timestamp"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"]
                }

            offset += len(rows)
            if len(rows) < chunk_size:
                break

candle_replay = HistoricalMarketReplayIterator()
