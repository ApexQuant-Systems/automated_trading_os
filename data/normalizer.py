# Component Manifest Contract Header
__module_name__ = "market_data_normalization_engine"
__build_version__ = "4.3.0-stable"
__spec_contract_hash__ = "0x07_data_normalizer_core"
__regression_suite_hash__ = "0x07_data_normalizer_verify"

from typing import List, Dict, Any
from utils.database import db
from logs.logger import logger

class MarketDataNormalizer:
    """Detects and repairs temporal gaps within historical asset price tables."""

    def get_timeframe_delta_seconds(self, timeframe: str) -> int:
        """Maps standard timeframe character codes to absolute second units."""
        mapping = {"15M": 15 * 60, "1H": 60 * 60, "1D": 24 * 60 * 60}
        if timeframe not in mapping:
            raise ValueError(f"Unsupported timeframe horizon specified: {timeframe}")
        return mapping[timeframe]

    def repair_gaps(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Identifies sequence discontinuities and injects forward-filled data rows."""
        logger.info(f"Auditing temporal consistency for asset: {symbol} | Timeframe: {timeframe}")
        
        delta_seconds = self.get_timeframe_delta_seconds(timeframe)
        metrics = {"checked_bars": 0, "gaps_repaired": 0}

        with db.connection() as conn:
            rows = conn.execute("""
                SELECT timestamp, open, high, low, close, volume 
                FROM market_data 
                WHERE symbol = ? AND timeframe = ? 
                ORDER BY timestamp ASC
            """, (symbol, timeframe)).fetchall()

            if len(rows) < 2:
                logger.warning(f"Insufficient history sequences found to run structural audit for {symbol}")
                return metrics

            metrics["checked_bars"] = len(rows)
            insert_records = []

            for i in range(len(rows) - 1):
                current_ts = rows[i]["timestamp"]
                next_ts = rows[i+1]["timestamp"]
                expected_next_ts = current_ts + delta_seconds

                while next_ts > expected_next_ts:
                    metrics["gaps_repaired"] += 1
                    fill_price = rows[i]["close"]
                    
                    insert_records.append((
                        symbol, timeframe, expected_next_ts,
                        fill_price, fill_price, fill_price, fill_price, 0.0
                    ))
                    expected_next_ts += delta_seconds

            if insert_records:
                conn.executemany("""
                    INSERT OR IGNORE INTO market_data (symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, insert_records)
                
        logger.info(f"Normalization Complete -> Checked: {metrics['checked_bars']} | Injected Repairs: {metrics['gaps_repaired']}")
        return metrics

data_normalizer = MarketDataNormalizer()
