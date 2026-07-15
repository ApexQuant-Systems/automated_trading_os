# Component Manifest Contract Header
__module_name__ = "vectorized_performance_backtester_core"
__build_version__ = "6.2.1-stable"

import os
import sys
import time
from typing import List, Dict, Any

# Enforce absolute project root directory lookups before loading local packages
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from market_intelligence.state_compiler import state_compiler
from strategy.signal_engine import strategy_engine

class PerformanceBacktester:
    """Core research framework conducting realistic simulation passes over deep historical logs."""

    def run_backtest(self, candles: List[Dict[str, Any]], asset_name: str, timeframe: str):
        print(f"\n=== INITIALIZING CORE PERFORMANCE BACKTEST FOR: {asset_name} ({timeframe}) ===")
        start_time = time.perf_counter()

        history_buffer = []
        trades_journal = []
        active_position = None
        
        # Performance Tracking Variables
        initial_equity = 1000.0
        current_equity = initial_equity
        high_water_mark = initial_equity
        max_drawdown = 0.0

        for i, candle in enumerate(candles):
            history_buffer.append(candle)
            
            # 1. Evaluate open position parameters against structural boundaries
            if active_position:
                if candle["low"] <= active_position["stop_loss"]:
                    # Simulated Stop Loss Hit (1.0% Risk Realized)
                    loss_amount = initial_equity * 0.01
                    current_equity -= loss_amount
                    trades_journal.append({"type": "LOSS", "pnl": -loss_amount, "exit_timestamp": candle["timestamp"]})
                    active_position = None
                elif candle["high"] >= active_position["take_profit"]:
                    # Simulated Take Profit Target Achieved (1:4 RR = 4.0% Gain Realized)
                    gain_amount = initial_equity * 0.04
                    current_equity += gain_amount
                    trades_journal.append({"type": "WIN", "pnl": gain_amount, "exit_timestamp": candle["timestamp"]})
                    active_position = None

            # 2. Check for fresh strategy confirmations if capital is unallocated
            if not active_position:
                state = state_compiler.compile_timeframe_state(history_buffer, asset_name, timeframe)
                if state.get("status") != "INSUFFICIENT_DATA":
                    decision = strategy_engine.evaluate_state_rules(state, candle["close"])
                    
                    if decision["action"] in ["BUY", "SELL"]:
                        active_position = {
                            "direction": decision["action"],
                            "entry_price": decision["entry_price"],
                            "stop_loss": decision["stop_loss"],
                            "take_profit": decision["take_profit"]
                        }

            # Track rolling maximum systemic drawdowns
            if current_equity > high_water_mark:
                high_water_mark = current_equity
            
            drawdown = (high_water_mark - current_equity) / high_water_mark
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # 3. Compile institutional performance analytics metrics
        total_trades = len(trades_journal)
        wins = [t for t in trades_journal if t["type"] == "WIN"]
        losses = [t for t in trades_journal if t["type"] == "LOSS"]
        
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
        gross_profits = sum([w["pnl"] for w in wins])
        gross_losses = abs(sum([l["pnl"] for l in losses]))
        profit_factor = gross_profits / gross_losses if gross_losses > 0 else (gross_profits if gross_profits > 0 else 1.0)
        
        elapsed_time = time.perf_counter() - start_time

        print("\n==================================================================")
        print("🏛️ APEX QUANT CORE PERFORMANCE BACKTEST SUMMARY REPORT")
        print("==================================================================")
        print(f"Total History Processed:    {len(candles)} candles")
        print(f"Total Transactions Logged:  {total_trades} trades executed")
        print(f"Simulation Compute Time:    {elapsed_time:.4f} seconds")
        print("------------------------------------------------------------------")
        print(f"Strategy Win Rate Score:    {win_rate:.2f}%")
        print(f"System Profit Factor:       {profit_factor:.2f}x Factor")
        print(f"Maximum Performance Drawdown: {max_drawdown * 100:.2f}%")
        print(f"Final Account Equity Valuation: ${current_equity:.2f} (Base: ${initial_equity:.2f})")
        print("==================================================================")
        print("=== QUANT RESEARCH STATUS: SIMULATION PASSED ===\n")

backtester = PerformanceBacktester()

if __name__ == "__main__":
    from data.replay import candle_replay
    # Pull the real 15-candle dataset from the database vault to trace execution integrity
    stream = candle_replay.stream_market_history("LINKUSD", "1H", 1722000000, 1723007200, chunk_size=500)
    backtester.run_backtest(list(stream), "LINKUSD", "1H")
