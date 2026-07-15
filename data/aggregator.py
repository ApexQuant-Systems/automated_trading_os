# Component Manifest Contract Header
__module_name__ = "multi_timeframe_candle_aggregator"
__build_version__ = "4.4.0-stable"
__spec_contract_hash__ = "0x08_mtf_aggregator_core"
__regression_suite_hash__ = "0x08_mtf_aggregator_verify"

from typing import List, Dict, Any
from utils.database import db
from data.loader import data_loader
from logs.logger import logger

class MultiTimeframeAggregator:
    """Provides pure mathematical translation layers to synthesize higher timeframe price metrics locally."""

    def get_timeframe_seconds(self, timeframe: str) -> int:
        """Returns exact structural time windows translated into absolute seconds metrics."""
        mapping = {"15M": 15 * 60, "1H": 60 * 60, "4H": 4 * 60 * 60, "1D": 24 * 60 * 60}
        if timeframe not in mapping:
            raise ValueError(f"Target timeframe notation specified is unsupported: {timeframe}")
        return mapping[timeframe]

    def aggregate_local_data(self, symbol: str, source_tf: str, target_tf: str) -> Dict[str, int]:
        """Queries base bars from disk storage, applies time grouping calculations, and saves the new arrays."""
        source_delta = self.get_timeframe_seconds(source_tf)
        target_delta = self.get_timeframe_seconds(target_tf)

        if source_delta >= target_delta:
            raise ValueError("Aggregation source interval must be strictly shorter than targeted framework window.")

        logger.info(f"Synthesizing higher timeframe arrays for asset: {symbol} | {source_tf} -> {target_tf}")

        with db.connection() as conn:
            rows = conn.execute("""
                SELECT timestamp, open, high, low, close, volume 
                FROM market_data 
                WHERE symbol = ? AND timeframe = ? 
                ORDER BY timestamp ASC
            """, (symbol, source_tf)).fetchall()

        if not rows:
            logger.warning(f"No lower historical database rows discovered for source selection: {symbol} [{source_tf}]")
            return {"attempted": 0, "inserted": 0, "rejected": 0}

        aggregated_bars: List[Dict[str, Any]] = []
        current_window_ts = rows[0]["timestamp"] - (rows[0]["timestamp"] % target_delta)
        window_bars = []

        for row in rows:
            bar_ts = row["timestamp"]
            
            if bar_ts >= current_window_ts + target_delta:
                if window_bars:
                    aggregated_bars.append(self._process_window(symbol, target_tf, current_window_ts, window_bars))
                    window_bars.clear()
                current_window_ts = bar_ts - (bar_ts % target_delta)

            window_bars.append(row)

        if window_bars:
            aggregated_bars.append(self._process_window(symbol, target_tf, current_window_ts, window_bars))

        return data_loader.ingress_batch(aggregated_bars)

    def _process_window(self, symbol: str, timeframe: str, window_ts: int, bars: List[Any]) -> Dict[str, Any]:
        """Executes invariant mathematical conversions across isolated window bar arrays."""
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": window_ts,
            "open": bars[0]["open"],
            "high": max(b["high"] for b in bars),
            "low": min(b["low"] for b in bars),
            "close": bars[-1]["close"],
            "volume": sum(b["volume"] for b in bars)
        }

candle_aggregator = MultiTimeframeAggregator()
