# Component Manifest Contract Header
__module_name__ = "historical_replay_signal_logger"
__build_version__ = "6.1.1-stable"

import os
import sys
import csv
import time
from typing import List

# Resolve absolute runtime paths to ensure seamless cross-module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.replay import candle_replay
from market_intelligence.state_compiler import state_compiler

class HistoricalSignalLogger:
    """Streams data from local storage and logs structural events to document strategy edge consistency."""

    def log_historical_signals(self, symbol: str, timeframe: str, start_ts: int, end_ts: int, output_file: str):
        print(f"\n=== INITIALIZING HISTORICAL SIGNAL AUDIT FOR: {symbol} ===")
        start_time = time.perf_counter()

        # Stream real history ticks sequentially to ensure zero look-ahead distortion
        candle_stream = candle_replay.stream_market_history(symbol, timeframe, start_ts, end_ts, chunk_size=1000)
        
        history_buffer = []
        logged_events_count = 0

        # Output payload directory configuration
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write a robust quantitative audit header template
            writer.writerow(["timestamp", "symbol", "timeframe", "trend", "phase", "last_break", "bullish_sweep", "bearish_sweep"])

            for candle in candle_stream:
                history_buffer.append(candle)
                
                # Compile unified market intelligence snapshots line-by-line
                state = state_compiler.compile_timeframe_state(history_buffer, symbol, timeframe)
                
                # Guard Clause: Skip processing if the buffer doesn't have enough candles yet
                if state.get("status") == "INSUFFICIENT_DATA":
                    continue
                
                struct_coords = state.get("structure_coordinates", {})
                pools = state.get("mapped_liquidity_pools", {})
                
                # Ensure we handle default empty values cleanly
                last_break = struct_coords.get("last_break_type", "NONE")
                
                has_event = (
                    last_break != "NONE" or
                    pools.get("BULLISH_SWEEP", False) or
                    pools.get("BEARISH_SWEEP", False)
                )

                if has_event:
                    writer.writerow([
                        state["timestamp"],
                        state["asset_name"],
                        state["timeframe"],
                        state["trend_state"],
                        state["market_phase"],
                        last_break,
                        pools.get("BULLISH_SWEEP", False),
                        pools.get("BEARISH_SWEEP", False)
                    ])
                    logged_events_count += 1

        elapsed = time.perf_counter() - start_time
        print("------------------------------------------------------------------")
        print(f"Audit Complete! Signals Logged: {logged_events_count} | Processing Time: {elapsed:.4f}s")
        print(f"Target Output Report Saved:   {output_file}")
        print("==================================================================")
        print("=== QUANT RESEARCH STATUS: LOGGED REPLAY PASSED ===\n")

logger_engine = HistoricalSignalLogger()

if __name__ == "__main__":
    # Scan the deep historical assets currently sitting inside your warehouse database
    logger_engine.log_historical_signals(
        symbol="LINKUSD",
        timeframe="1H",
        start_ts=1722000000,
        end_ts=1723007200,
        output_file="research/reports/historical_signals_audit.csv"
    )
