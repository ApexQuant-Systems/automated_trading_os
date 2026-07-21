# Component Manifest Contract Header
__module_name__ = "production_warehouse_loader"
__build_version__ = "1.1.0-stable"
__spec_contract_hash__ = "0x109_production_loader_v3"

from typing import List, Tuple
from utils.database import db_manager

class WarehouseLoader:
    """Streams normalized canonical time-series arrays dynamically into partitioned storage layers."""

    def load_candles(self, symbol: str, asset_class: str, timeframe: str, job_id: str, candles: List[Tuple[int, float, float, float, float, float, float, int]]) -> int:
        """Commits processed candlestick records to their specific asset class partition table."""
        if not candles:
            return 0

        # Dynamically determine destination workspace table signature
        table_name = f"{asset_class.lower()}_candles"
        
        stmt = f"""
            INSERT OR REPLACE INTO {table_name} (
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
