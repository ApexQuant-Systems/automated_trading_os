# Component Manifest Contract Header
__module_name__ = "multi_asset_sync_matrix"
__build_version__ = "4.6.1-stable"
__spec_contract_hash__ = "0x10_sync_matrix_core"
__regression_suite_hash__ = "0x10_sync_matrix_verify"

from typing import List, Dict, Any, Generator
from data.replay import candle_replay
from logs.logger import logger

class MultiAssetSyncMatrix:
    """Synchronizes historical candlestick feeds across multiple assets onto a clean, unified time grid."""

    def stream_synchronized_market(self, symbols: List[str], timeframe: str, start_ts: int, end_ts: int) -> Generator[Dict[str, Any], None, None]:
        """Aligns data streams chronologically, using historical forward-filled states to resolve liquidity gaps."""
        logger.info(f"Initializing Multi-Asset Temporal Sync Matrix for targets: {symbols} | Horizon: [{start_ts} -> {end_ts}]")
        
        # 1. Initialize independent data playback iterators for each asset target
        streams = {
            sym: candle_replay.stream_market_history(sym, timeframe, start_ts, end_ts, chunk_size=1000)
            for sym in symbols
        }
        
        # Caches to preserve the next incoming bar (used to determine chronological grid steps)
        current_state_cache: Dict[str, Any] = {sym: None for sym in symbols}
        
        # Chronological buffer storing only the last EMITTED historical state to eliminate look-ahead bias
        last_emitted_cache: Dict[str, Any] = {sym: None for sym in symbols}
        
        active_iterators = {sym: True for sym in symbols}

        # Seed initial state cache values
        for sym in symbols:
            try:
                current_state_cache[sym] = next(streams[sym])
            except StopIteration:
                active_iterators[sym] = False
                current_state_cache[sym] = None

        while any(active_iterators.values()):
            # Find the absolute oldest active timestamp among the current candle states
            valid_timestamps = [
                current_state_cache[sym]["timestamp"] 
                for sym in symbols 
                if current_state_cache[sym] is not None
            ]
            
            if not valid_timestamps:
                break
                
            current_grid_ts = min(valid_timestamps)
            snapshot: Dict[str, Any] = {"timestamp": current_grid_ts, "data": {}}

            for sym in symbols:
                bar = current_state_cache[sym]
                
                if bar and bar["timestamp"] == current_grid_ts:
                    # Perfect temporal alignment discovered
                    snapshot["data"][sym] = bar
                    
                    # Update past tracking records cache
                    last_emitted_cache[sym] = bar
                    
                    # Advance the target asset stream forward by one step
                    try:
                        current_state_cache[sym] = next(streams[sym])
                    except StopIteration:
                        active_iterators[sym] = False
                        current_state_cache[sym] = None
                else:
                    # Liquidity Gap detected at this timestamp grid point.
                    # Execute Forward-Fill using the asset's last EMITTED historical close price.
                    last_known_bar = last_emitted_cache[sym]
                    if last_known_bar:
                        snapshot["data"][sym] = {
                            "symbol": sym,
                            "timeframe": timeframe,
                            "timestamp": current_grid_ts,
                            "open": last_known_bar["close"],
                            "high": last_known_bar["close"],
                            "low": last_known_bar["close"],
                            "close": last_known_bar["close"],
                            "volume": 0.0  # Safe volume initialization rule
                        }
                    else:
                        # Market initialization boundary: no historical bars available yet
                        snapshot["data"][sym] = None

            yield snapshot

sync_matrix = MultiAssetSyncMatrix()
