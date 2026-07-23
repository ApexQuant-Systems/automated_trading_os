"""
APEX Quant OS - Dual-Layer Visual Backtest Execution (v3.0)
Processes historical candles and generates a dual-layer structure chart image for visual verification.
"""

from market_data.warehouse.replay import ReplayLoader
from market_language.market_structure import Candle, MarketStructurePolicy, StructureCompiler
from market_language.market_structure.visualizer import StructureVisualizer


def run_audit():
    print("==================================================================")
    print("   APEX QUANT OS: GENERATING DUAL-LAYER STRUCTURE AUDIT CHART    ")
    print("==================================================================")

    # Fetch recent 150 BTC 4H candles for clear chart resolution
    raw_candles = ReplayLoader.get_history(symbol="BTCUSDT", timeframe="4H", limit=150)
    
    candles = [
        Candle(
            timestamp=c["timestamp"],
            open=c["open"],
            high=c["high"],
            low=c["low"],
            close=c["close"],
            volume=c["volume"]
        )
        for c in raw_candles
    ]

    policy = MarketStructurePolicy(fractal_left_bars=2, fractal_right_bars=2, break_confirmation="STRICT_BODY")
    compiler = StructureCompiler(policy=policy)
    
    # Compile State
    state = compiler.compile(candles, symbol="BTCUSDT", timeframe="4H")

    # Render Visual Chart Image
    chart_path = StructureVisualizer.plot_structure(candles, state, output_filename="btc_structure_audit.png")

    print(f"✅ Visual Chart Generated Successfully: {chart_path}")
    print(f"   ├── External Swings Rendered: {len(state.external_swings)}")
    print(f"   ├── Internal Swings Rendered: {len(state.internal_swings)}")
    print(f"   ├── Events Rendered: {len(state.recent_events)}")
    print(f"   └── Current Trend: {state.trend.direction.value}")
    print("==================================================================")


if __name__ == "__main__":
    run_audit()
