# Component Manifest Contract Header
__module_name__ = "historical_warehouse_loader"
__build_version__ = "1.1.0-stable"
__spec_contract_hash__ = "0x11_historical_loader_core"
__regression_suite_hash__ = "0x11_historical_loader_verify"

import os
import sys
import time
from typing import List, Dict, Any

# Resolve absolute path execution contexts to maintain cross-folder importing transparency
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.database import db
from logs.logger import logger

class HistoricalWarehouseLoader:
    """Ingress engine managing the data cleansing and seeding of multi-year asset history rows."""

    def load_and_seed_history(self, symbol: str, timeframe: str, candle_data: List[Dict[str, Any]], exchange: str = "VANTAGE") -> Dict[str, Any]:
        """Validates incoming candle streams, appends structural metadata, and bulk-saves to database."""
        start_time = time.perf_counter()
        
        if not candle_data:
            logger.warning(f"Ingress warning: Empty history array passed for {symbol} ({timeframe}).")
            return {"status": "EMPTY_PAYLOAD", "records_seeded": 0}

        records_seeded = 0
        current_time_ts = int(time.time())

        # Establish single transactional database mapping connection context
        with db.connection() as conn:
            for candle in candle_data:
                # Enforce strict field isolation compliance rules
                timestamp = int(candle["timestamp"])
                open_p = float(candle["open"])
                high_p = float(candle["high"])
                low_p = float(candle["low"])
                close_p = float(candle["close"])
                volume_v = float(candle["volume"])
                spread_v = float(candle.get("spread", 0.0))

                # Data Purity Check: Catch invalid candle structures before they corrupt the tables
                if high_p < low_p or high_p < max(open_p, close_p) or low_p > min(open_p, close_p):
                    logger.error(f"Data Purity Violation: Corrupt candle shapes blocked at timestamp {timestamp}")
                    continue

                # Inject baseline data quality metrics score parameters natively
                quality_score = 100.0
                if volume_v <= 0:
                    quality_score -= 20.0  # De-rate low-liquidity anomaly windows
                if spread_v > (close_p * 0.01):
                    quality_score -= 10.0  # De-rate extreme spread volatility tracking anomalies

                conn.execute("""
                    INSERT OR REPLACE INTO market_data (
                        symbol, timeframe, timestamp, open, high, low, close, volume, spread,
                        provider, exchange, timezone, ingestion_time, quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol, timeframe, timestamp, open_p, high_p, low_p, close_p, volume_v, spread_v,
                    "HISTORICAL_VAULT", exchange.upper(), "UTC", current_time_ts, quality_score
                ))
                records_seeded += 1

        elapsed = time.perf_counter() - start_time
        logger.info(f"Ingress complete: {records_seeded} bars seeded for {symbol} [{timeframe}] in {elapsed:.4f}s.")
        
        return {
            "status": "SUCCESS",
            "records_seeded": records_seeded,
            "elapsed_seconds": elapsed
        }

historical_loader = HistoricalWarehouseLoader()
