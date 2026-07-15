# Component Manifest Contract Header
__module_name__ = "historical_data_loader"
__build_version__ = "4.1.0-stable"
__spec_contract_hash__ = "0x05_data_loader_core"
__regression_suite_hash__ = "0x05_data_loader_verify"

from typing import List, Dict, Any
from utils.database import db
from logs.logger import logger

class HistoricalDataLoader:
    """Ingests, validates, and batch-loads historical multi-timeframe OHLCV data rings."""
    
    def validate_bar(self, bar: Dict[str, Any]) -> bool:
        """Enforces physical price constraints to ensure data integrity before ingestion."""
        required_keys = {"symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume"}
        if not required_keys.issubset(bar.keys()):
            return False
            
        # Physical boundary checks: Prices and volume must be positive
        if any(bar[k] <= 0 for k in ["open", "high", "low", "close", "volume"]):
            return False
            
        # Mathematical invariance check: High cannot be lower than low, open, or close
        if bar["high"] < bar["low"] or bar["high"] < bar["open"] or bar["high"] < bar["close"]:
            return False
            
        # Mathematical invariance check: Low cannot be higher than open or close
        if bar["low"] > bar["open"] or bar["low"] > bar["close"]:
            return False
            
        return True

    def ingress_batch(self, data_batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Processes and batch-inserts validated historical rows using write transaction contexts."""
        metrics = {"attempted": len(data_batch), "inserted": 0, "rejected": 0}
        
        query = """
            INSERT OR IGNORE INTO market_data (symbol, timeframe, timestamp, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        insert_records = []
        for bar in data_batch:
            if self.validate_bar(bar):
                insert_records.append((
                    bar["symbol"], bar["timeframe"], bar["timestamp"],
                    bar["open"], bar["high"], bar["low"], bar["close"], bar["volume"]
                ))
            else:
                metrics["rejected"] += 1
                
        if insert_records:
            try:
                with db.connection() as conn:
                    cursor = conn.executemany(query, insert_records)
                    metrics["inserted"] = cursor.rowcount
            except Exception as e:
                logger.error("Failed to commit historical data ingestion batch record set.", e)
                raise e
                
        logger.info(f"Ingress Summary -> Attempted: {metrics['attempted']} | Inserted: {metrics['inserted']} | Rejected: {metrics['rejected']}")
        return metrics

# Instantiated utility handler for global framework access
data_loader = HistoricalDataLoader()
