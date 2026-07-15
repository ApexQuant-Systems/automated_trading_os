# Component Manifest Contract Header
__module_name__ = "csv_data_streaming_adapter"
__build_version__ = "4.2.0-stable"
__spec_contract_hash__ = "0x06_csv_stream_core"
__regression_suite_hash__ = "0x06_csv_stream_verify"

import csv
import os
from typing import Dict, Any, Generator, List
from data.loader import data_loader
from logs.logger import logger

class CSVStreamingAdapter:
    """Streams large historical datasets from disk into ingestion pipelines using constant RAM footprints."""

    def stream_lines(self, file_path: str, symbol: str, timeframe: str) -> Generator[Dict[str, Any], None, None]:
        """Reads CSV files line-by-line using standard stream generators to prevent memory bloat."""
        if not os.path.exists(file_path):
            logger.error(f"Target data file not found on disk storage engine: {file_path}")
            return

        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    yield {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "timestamp": int(row["timestamp"]),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row["volume"])
                    }
                except (KeyError, ValueError):
                    # Skip malformed data rows or header contamination lines cleanly
                    continue

    def load_csv_in_chunks(self, file_path: str, symbol: str, timeframe: str, chunk_size: int = 10000) -> Dict[str, int]:
        """Groups data points into transaction chunks to optimize database writing latency."""
        logger.info(f"Initiating memory-optimized historical load sequence for asset: {symbol} | Target: {file_path}")
        
        metrics = {"attempted": 0, "inserted": 0, "rejected": 0}
        buffer: List[Dict[str, Any]] = []

        for bar in self.stream_lines(file_path, symbol, timeframe):
            metrics["attempted"] += 1
            buffer.append(bar)

            if len(buffer) >= chunk_size:
                chunk_metrics = data_loader.ingress_batch(buffer)
                metrics["inserted"] += chunk_metrics["inserted"]
                metrics["rejected"] += chunk_metrics["rejected"]
                buffer.clear()

        # Flush remaining data trailing rows left inside the memory stack
        if buffer:
            chunk_metrics = data_loader.ingress_batch(buffer)
            metrics["inserted"] += chunk_metrics["inserted"]
            metrics["rejected"] += chunk_metrics["rejected"]
            buffer.clear()

        logger.info(f"Ingress Transaction Complete -> Total Attempted: {metrics['attempted']} | Inserted: {metrics['inserted']} | Rejected: {metrics['rejected']}")
        return metrics

csv_adapter = CSVStreamingAdapter()
