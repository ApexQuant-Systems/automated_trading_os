# Component Manifest Contract Header
__module_name__ = "production_warehouse_loader"
__build_version__ = "1.0.1-stable"
__spec_contract_hash__ = "0x109_production_loader_v2"

from typing import List, Tuple
from utils.database import db_manager

class WarehouseLoader:
    """Streams normalized canonical time-series arrays directly into partitioned storage layers."""

    def load_crypto_candles(self, symbol: str, timeframe: str, job_id: str, candles: List[Tuple[int, float, float, float, float, float, float, int]]) -> int:
        """Commits processed crypto candlestick blocks using optimized SQLite batch execution pools."""
        if not candles:
            return 0

        stmt = """
            INSERT OR REPLACE INTO crypto_candles (
                timestamp, symbol, timeframe, open, high, low, close, volume, quote_volume, trade_count, job_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        payload = [
            (c[0], symbol, timeframe, c[1], c[2], c[3], c[4], c[5], c[6], c[7], job_id)
            for c in candles
        ]

        with db_manager.price_db() as conn:
            conn.executemany(stmt, payload)
            
        return len(payload)

warehouse_loader = WarehouseLoader()
