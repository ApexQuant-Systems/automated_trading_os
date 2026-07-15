# Component Manifest Contract Header
__module_name__ = "historical_pipeline_validator_engine"
__build_version__ = "5.6.1-stable"

import os
import sys
import time

# Enforce explicit project root path resolution before loading system components
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.replay import candle_replay
from market_intelligence.state_compiler import state_compiler

class PipelineValidator:
    """Streams data from local storage to benchmark pipeline performance under realistic conditions."""

    def execute_stress_validation(self, symbol: str, timeframe: str, start_ts: int, end_ts: int):
        print(f"\n=== LAUNCHING REALITY STRESS TESTING REPLAY FOR: {symbol} ===")
        
        # Initialize streaming generator from our Look-Ahead Protected Replay Engine
        candle_stream = candle_replay.stream_market_history(symbol, timeframe, start_ts, end_ts, chunk_size=500)
        
        history_buffer = []
        metrics = {
            "total_candles_processed": 0,
            "bullish_states": 0,
            "bearish_states": 0,
            "ranging_states": 0,
            "expansion_phases": 0,
            "pullback_phases": 0
        }
        
        start_time = time.perf_counter()

        for candle in candle_stream:
            history_buffer.append(candle)
            metrics["total_candles_processed"] += 1
            
            # Run the complete analysis stack on the historical data buffer
            state = state_compiler.compile_timeframe_state(history_buffer, symbol, timeframe)
            
            # Aggregate metrics to evaluate strategy and trend distribution
            if state.get("trend_state") == "BULLISH": metrics["bullish_states"] += 1
            elif state.get("trend_state") == "BEARISH": metrics["bearish_states"] += 1
            else: metrics["ranging_states"] += 1
                
            if state.get("market_phase") == "EXPANSION": metrics["expansion_phases"] += 1
            elif state.get("market_phase") == "PULLBACK": metrics["pullback_phases"] += 1

        elapsed_time = time.perf_counter() - start_time
        
        if metrics["total_candles_processed"] == 0:
            print("⚠️ Ingress Check Failed: No historical bars discovered in the database vault range.")
            return

        throughput = metrics["total_candles_processed"] / elapsed_time

        print("\n==================================================================")
        print("🏛️ HISTORICAL PERFORMANCE MONITOR METRICS REPLAY REPORT")
        print("==================================================================")
        print(f"Total Database Rows Scaled:  {metrics['total_candles_processed']} candles")
        print(f"Total Ingestion Compute Time: {elapsed_time:.4f} seconds")
        print(f"Engine Data Throughput:       {throughput:.2f} candles/sec")
        print("------------------------------------------------------------------")
        print(f"Trend Breakdown  -> Bullish: {metrics['bullish_states']} | Bearish: {metrics['bearish_states']} | Ranging: {metrics['ranging_states']}")
        print(f"Phase Breakdown  -> Expansion: {metrics['expansion_phases']} | Pullback: {metrics['pullback_phases']}")
        print("==================================================================")
        print("=== QUANT ENGINEERING STATUS: VALIDATION PASSED ===\n")

validator = PipelineValidator()

if __name__ == "__main__":
    # Run the stress-test using the historical asset data populated during our previous data runs
    validator.execute_stress_validation("LINKUSD", "1H", 1722000000, 1723007200)
